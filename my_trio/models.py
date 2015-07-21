# -*- coding: utf8 -*-

from peewee import Model, CharField, DateTimeField, ForeignKeyField, TextField, datetime as peewee_datetime, IntegerField, DecimalField, BooleanField
from playhouse.pool import PooledPostgresqlExtDatabase

from config import DB_CONFIG
from my_trio.utils import Struct
from constants import WithdrawStatus, InvoiceStatus
from hashlib import sha1  # added by Banit Vitalii

db = PooledPostgresqlExtDatabase(**DB_CONFIG)
db.commit_select = True
db.autorollback = True


class _Model(Model):
        class Meta:
            database = db

        def __repr__(self):
            #data = ", ".join(["%s: %s" % (key, unicode(value).encode('utf8') if value else None) for key, value in self._data.items()])
            #return "{class_name}: {{ {data} }}".format(class_name = self.__class__.__name__, data = data)
            return "{class_name}(id={id})".format(class_name=self.__class__.__name__, id=self.id)

        def to_dict(self):
            return dict(self._data.items())

        def to_struct(self):
            return Struct(**self.to_dict())

        def info(self):
            # TODO return short info for merchant
            return self.to_struct()

        @classmethod
        def get_by_id(cls, id):
            try:
                return cls.get(cls.id == id)
            except cls.DoesNotExist:
                return None

        def save(self, **kwds):
            with db.transaction() as txn:
                Model.save(self, **kwds)

        def delete_me(self):
            with db.transaction() as txn:
                self.delete_instance()


class Currency(_Model):
    class Meta:
        db_table = "currency"

    code = IntegerField(primary_key=True)
    alias = CharField()


class CurrencyRate(_Model):
    class Meta:
        db_table = "currency_rates"

    from_currency = IntegerField()
    to_currency = IntegerField()
    input_rate = DecimalField()	# курс, используемый при рассчетах на ввод
    input_fee_percent = DecimalField()	# процент конвертационной комиссии, при рассчетах на ввод
    output_rate = DecimalField()	# курс, используемый при рассчетах на вывод
    output_fee_percent = DecimalField()	# процент конвертационной комиссии, при рассчетах на вывод
    updated = DateTimeField(default=peewee_datetime.datetime.now)
    protocol_config = TextField(null=True)

    @staticmethod
    def get_exch_info(from_currency, to_currency):
        try:
            return CurrencyRate.select().where(CurrencyRate.from_currency==from_currency, CurrencyRate.to_currency==to_currency).get()
        except CurrencyRate.DoesNotExist:
            return None


class Account(_Model):
    class Meta:
        db_table = "accounts"

    email = CharField(unique=True)
    registered_on = DateTimeField(default=peewee_datetime.datetime.now())
    password = CharField()
    description = CharField(null=True)

    def set_password(self, password):
        self.password = sha1(password).hexdigest()


class Paysystem(_Model):
    class Meta:
        db_table = "paysystems"

    name = CharField()
    config = TextField(null=True)


class InvoicePayway(_Model):
    class Meta:
        db_table = "invoice_payways"

    name = CharField()
    paysystem = ForeignKeyField(Paysystem)
    currency = IntegerField()
    is_used = BooleanField(default=False)
    ps_fee_config = TextField() # {"percent": 3.5, "fix": 5}
    margin_config = TextField() #  {"percent": 2.5, "fix": 0.0}
    protocol_config = TextField()


class WithdrawPayway(_Model):
    class Meta:
        db_table = "withdraw_payways"

    name = CharField()
    paysystem = ForeignKeyField(Paysystem)
    currency = IntegerField()
    is_used = BooleanField(default=False)
    ps_fee_config = TextField() # {"percent": 3.5, "fix": 5}
    margin_config = TextField() #  {"percent": 2.5, "fix": 0.0}
    protocol_config = TextField()
    account_info_config = TextField(null=True)
    is_fee_up = BooleanField() # признак, как работает ПС - снимает комиссию как внешнюю или внутреннюю. True - значит внешняя комиссия, ПС списывает с нас свою комиссию отдельно от тела платежа, мы отправляем на ПС сам платеж без включения в него комиссии ПС;


class Shop(_Model):
    class Meta:
        db_table = "shops"

    id = CharField(primary_key=True)
    account = ForeignKeyField(Account)
    token = CharField()
    description = CharField(null=True)
    url = CharField()
    ip_list = TextField(null=True) # json-list ['127.0.0.1']


class ShopLegalInvoicePaywayConfig(_Model):
    class Meta:
        db_table = "shop_legal_invoice_payway_config"
        indexes = (
            # create a unique on shop/payway
            (('shop', 'payway',), True),
        )

    shop = ForeignKeyField(Shop)
    payway = ForeignKeyField(InvoicePayway)
    is_active = BooleanField(default=True)
    created = DateTimeField(default=peewee_datetime.datetime.now)
    fee_part_config = TextField() # {"percent_part": 0..1, "fix_part": 1 or 0}
    margin_config = TextField(null=True) # {"percent": 2.5, "fix": 0.0}
    ps_config = TextField(null=True) # для хранения информации по специальным ПН (ЯД, Киви), в том числе аналогично Payway.ps_fee_config
                                     # {"ps_fee_config": {"percent": 3.5, "fix": 5}, "ps_protocol_config": {"qiwi_shop_id": "12345"}}


class ShopLegalWithdrawPaywayConfig(_Model):
    class Meta:
        db_table = "shop_legal_withdraw_payway_config"
        indexes = (
            # create a unique on shop/payway
            (('shop', 'payway',), True),
        )

    shop = ForeignKeyField(Shop)
    payway = ForeignKeyField(WithdrawPayway)
    is_active = BooleanField(default=True)
    created = DateTimeField(default=peewee_datetime.datetime.now)
    direct_payment = BooleanField(default=False) # отправлять ли сразу вывод на ПС или ожидать модерации


class Invoice(_Model):
    class Meta:
        db_table = "invoices"

    shop = ForeignKeyField(Shop)
    payway = ForeignKeyField(InvoicePayway)
    status = IntegerField(default=InvoiceStatus.New)
    created = DateTimeField(default=peewee_datetime.datetime.now)
    shop_invoice_id = CharField(null=True)
    shop_currency = IntegerField()
    shop_amount = DecimalField()
    description = CharField(null=True)
    add_ons = TextField(null=True)
    exch_rate = DecimalField()
    ps_currency = IntegerField()

    fee_percent = DecimalField() # итоговый % нашей комиссии по платежу
    shop_fee_percent = DecimalField() # итоговый % нашей комиссии по платежу, который платит касса
    client_fee_percent = DecimalField() # итоговый % нашей комиссии по платежу, который платит плательщик

    fee_fix = DecimalField() # итоговая фиксированная часть нашей комиссии
    shop_fee_fix = DecimalField() # итоговая фиксированная часть нашей комиссии, которую платит касса
    client_fee_fix = DecimalField() # итоговая фиксированная часть нашей комиссии, которую платит плательщик

    ps_amount = DecimalField() # сумма выставленного счета магазина в валюте платежной системы;4 зн после зпт; округление: математическое.
    exch_fee = DecimalField() # конвертационная комиссия (доход): Количество знаков после запятой: 4; округление: математическое.

    fee = DecimalField() # наша комиссия всего: Количество знаков после запятой: 4; округление: математическое.
    shop_fee = DecimalField() # наша комиссия, которую платит касса (мерчант): Количество знаков после запятой: 4; округление: математическое.
    client_fee = DecimalField() # наша комиссия, которую платит плательщик: Количество знаков после запятой: 4; округление: математическое.

    client_price = DecimalField() # сумма, выставленная плательщику для оплаты в валюте платежной системы: Количество знаков после запятой: 2; округление: математическое.
    ps_fee = DecimalField() # комиссия платежной системы в валюте ПС: Количество знаков после запятой: 2; округление: вверх.

    total_fee_inc = DecimalField() # комиссионный доход (без вычета комиссии платежных систем) в валюте ПС: Количество знаков после запятой: 4; округление: математическое.
    net_fee_inc = DecimalField() # чистый комиссионный доход в валюте ПС: Количество знаков после запятой: 4; округление: математическое.

    ps_refund = DecimalField() # сумма к зачислению в кассу в валюте платежной системы: Количество знаков после запятой: 4; округление: математическое.
    shop_refund = DecimalField() # сумма к зачислению в кассу в валюте кассы: Количество знаков после запятой: 2; округление: математическое.

    geller_invoice_id = IntegerField(null=True)
    processed = DateTimeField(null=True)
    ps_invoice_id = CharField(null=True)
    ps_processed = DateTimeField(null=True)
    ps_account_info = TextField(null=True)
    ps_info = TextField(null=True)

class Withdraw(_Model):
    class Meta:
        db_table = "withdraws"
        indexes = (
            # create a unique on shop/shop_payment_id
            (('shop', 'shop_payment_id',), True),
        )

    shop = ForeignKeyField(Shop)
    payway = ForeignKeyField(WithdrawPayway)
    status = IntegerField(default=WithdrawStatus.New)
    created = DateTimeField(default=peewee_datetime.datetime.now)
    shop_payment_id = CharField(null=True)
    shop_currency = IntegerField()

    account = TextField()
    account_details = TextField(null=True)
    description = CharField(null=True)
    add_ons = TextField(null=True)
    exch_rate = DecimalField()
    ps_currency = IntegerField()

    fee_percent = DecimalField() # процентная часть нашей комиссии за вывод средств
    fee_fix = DecimalField() # фиксированная часть нашей комиссии за вывод средств

    shop_amount = DecimalField() # сумма заявки на вывод средств в валюте кассы
    ps_amount = DecimalField() # сумма заявки на вывод средств в валюте платежной системы

    payee_receive = DecimalField() # сумма перечисления мерчанту в валюте платежной системы
    ps_transfer = DecimalField() # сумма перечисления на платежную систему, в валюте ПС
    ps_fee = DecimalField() # комиссия платежной системы в валюте платежной системы
    exch_fee = DecimalField() # конвертационная комиссия (доход ИК)
    fee = DecimalField() # всего наша комиссия за вывод в валюте платежной системы
    ps_write_off = DecimalField() # сумма списания с кошелька мерчанта в валюте ПС
    shop_write_off = DecimalField() # сумма списания с кошелька мерчанта в валюте кассы
    total_fee_inc = DecimalField() # всего наш доход в валюте ПС
    net_fee_inc = DecimalField() # чистый комиссионный доход ИК

    bing_invoice_id = IntegerField(null=True)
    processed = DateTimeField(null=True)
    ps_invoice_id = CharField(null=True)
    ps_processed = DateTimeField(null=True)
    ps_info = TextField(null=True)

    def careful_create(self, purse):
        with db.transaction() as txn:
            purse.frozen = self.shop_write_off
            purse.balance = float(purse.balance) - self.shop_write_off
            purse.save()
            self.save()
            txn.commit()


# purses
class ShopPurse(_Model):
    class Meta:
        db_table = "shop_purses"

    name = CharField()
    currency = IntegerField()
    shop = ForeignKeyField(Shop, related_name="purses")
    balance = DecimalField(default=0)
    frozen = DecimalField(default=0)


class PaysystemPurse(_Model):
    class Meta:
        db_table = "paysystem_purses"

    name = CharField()
    currency = IntegerField()
    paysystem = ForeignKeyField(Paysystem)
    balance = DecimalField(default=0)


class RealCurrencyPurse(_Model):
    class Meta:
        db_table = "real_currency_purses"

    name = CharField()
    currency = IntegerField()
    balance = DecimalField(default=0)


class VirtualCurrencyPurse(_Model):
    class Meta:
        db_table = "virtual_currency_purses"

    name = CharField()
    currency = IntegerField()
    balance = DecimalField(default=0)


class PaysystemTransaction(_Model):
    class Meta:
        db_table = "paysystem_transactions"
    '''
    id счета, в погашение которого поступили средства
    id кошелька с которого совершается перевод
    id кошелька на который совершается перевод
    время совершения операции перевода
    время получения уведомления о зачислении (время платежной системы)
    фактическая сумма поступления средств на счет
    ожидаемая сумма поступления насчет (берется из суммы счета в валюте ПС)
    комиссия платежной системы с системы за данную операцию фактическая
    комиссия платежной системы с системы за данную операцию ожидаемая
    баланс исходящего кошелька после совершения операции
    баланс входящего кошелька после совершения операции
    id операции в платежной системе
    аккаунт плательщика в платежной системе (номер карты, мобильный телефон номер кошелька)
    доп. информация от платежной системы.
    #статус
    '''
    invoice = ForeignKeyField(Invoice)
    source_purse = ForeignKeyField(RealCurrencyPurse)
    destination_purse = ForeignKeyField(PaysystemPurse)
    processed = DateTimeField()
    source_purse_balance = DecimalField()
    destination_purse_balance = DecimalField()
    ps_processed = DateTimeField()
    ps_amount = DecimalField()
    ps_fee = DecimalField() # фактическая
    ps_amount_calc = DecimalField() # invoice.client_price - invoice.ps_fee
    ps_fee_calc = DecimalField() # ожидаемая
    ps_transaction_id = CharField(null=True)
    ps_info = TextField(null=True)
    ps_account_info = TextField(null=True)


class ShopTransaction(_Model):
    class Meta:
        db_table = "shop_transactions"

    '''
    id счета, который вызвал пополнение баланса
    время совершения операции пополнения
    id пользовательского кошелька
    id кошелька общей электронной валюты
    сумма зачисления в валюте счета (берется из счета “сумма зачисления средств на кошелек”)
    баланс пользовательского кошелька, после операции
    баланс системного кошелька электронной валюты
    #комиссия системы за данную операцию
    #статус
    '''
    invoice = ForeignKeyField(Invoice)
    source_purse = ForeignKeyField(ShopPurse)
    destination_purse = ForeignKeyField(VirtualCurrencyPurse)
    amount = DecimalField()
    source_purse_balance = DecimalField()
    destination_purse_balance = DecimalField()
    #comission = DecimalField()


def init_db():
    try:
        db.connect()
        map(lambda l: db.drop_table(l, True), [CurrencyRate, ShopLegalInvoicePaywayConfig, ShopLegalWithdrawPaywayConfig, ShopTransaction, PaysystemTransaction, Invoice, Withdraw, ShopPurse, PaysystemPurse, VirtualCurrencyPurse, RealCurrencyPurse, Currency, InvoicePayway, WithdrawPayway, Paysystem, Shop, Account])
        print "tables dropped"
        db.create_tables([CurrencyRate, Currency, Paysystem, WithdrawPayway, InvoicePayway, Account, Shop, Invoice, ShopPurse, PaysystemPurse, VirtualCurrencyPurse, RealCurrencyPurse, ShopTransaction, PaysystemTransaction, ShopLegalInvoicePaywayConfig, ShopLegalWithdrawPaywayConfig, Withdraw])
        print "tables created"
    except:
        db.rollback()
        raise
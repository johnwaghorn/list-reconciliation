VALIDATORS = {
    "RECORD_TYPE": lambda x: (x, None),
    "REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": lambda x: (x, None),
    "TRADING_PARTNER_NHAIS_CIPHER": lambda x: (x, None),
    "DATE_OF_DOWNLOAD": lambda x: (x, None),
    "PRACTICE_SITE_NUMBER": lambda x: (x, None),
    "CLINCAL_SYSTEM_NUMBER": lambda x: (x, None),
    "NHS_NUMBER": lambda x: (x, None),
    "SURNAME": lambda x: (x, None),
    "FORENAMES": lambda x: (x, None),
    "PREV_SURNAME": lambda x: (x, None),
    "TITLE": lambda x: (x, None),
    "SEX_(1=MALE,2=FEMALE)": lambda x: (x, None),
    "DOB": lambda x: (x, None),
    "ADDRESS_LINE1": lambda x: (x, None),
    "ADDRESS_LINE2": lambda x: (x, None),
    "ADDRESS_LINE3": lambda x: (x, None),
    "ADDRESS_LINE4": lambda x: (x, None),
    "ADDRESS_LINE5": lambda x: (x, None),
    "POSTCODE": lambda x: (x, None),
    "DISTANCE": lambda x: (x, None),
}

INVALID = "_INVALID_"

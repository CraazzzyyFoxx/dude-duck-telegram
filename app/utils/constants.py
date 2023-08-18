OrderRenderBase = {
    "name": "base",
    "fields": [
        {
            "name": "Order",
            "fields": [
                {
                    "attr": "order_id",
                    "storage": [
                        "order"
                    ],
                    "format": None,
                    "before_value": None,
                    "after_value": None
                }
            ],
            "markdown_name": "<b>",
            "markdown_value": None,
            "separator": " "
        },
        {
            "name": "Description",
            "fields": [
                {
                    "attr": "boost_type",
                    "storage": [
                        "order"
                    ],
                    "format": None,
                    "before_value": None,
                    "after_value": None
                },
                {
                    "attr": "game",
                    "storage": [
                        "order"
                    ],
                    "format": None,
                    "before_value": None,
                    "after_value": None
                },
                {
                    "attr": "category",
                    "storage": [
                        "order"
                    ],
                    "format": None,
                    "before_value": None,
                    "after_value": None
                },
                {
                    "attr": "purchase",
                    "storage": [
                        "order"
                    ],
                    "format": None,
                    "before_value": None,
                    "after_value": None
                }
            ],
            "markdown_name": "<b>",
            "markdown_value": None,
            "separator": " "
        },
        {
            "name": "Additional Info",
            "fields": [
                {
                    "attr": "comment",
                    "storage": [
                        "order"
                    ],
                    "format": None,
                    "before_value": None,
                    "after_value": None
                }
            ],
            "markdown_name": "<b>",
            "markdown_value": None,
            "separator": " "
        }
    ],
    "separator": "<br>▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬<br>",
    "separator_field": "<br>"
}

OrderRenderEtaPrice = {
    "name": "eta-price",
    "fields": [
        {
            "name": "ETA",
            "fields": [
                {
                    "attr": "eta",
                    "storage": [
                        "order", "info"
                    ],
                    "format": None,
                    "before_value": None,
                    "after_value": None
                }
            ],
            "markdown_name": "<b>",
            "markdown_value": None,
            "separator": " "
        },
        {
            "name": "Price",
            "fields": [
                {
                    "attr": "price_booster_rub",
                    "storage": [
                        "order"
                    ],
                    "format": ".2f",
                    "before_value": None,
                    "after_value": "р."
                },
                {
                    "attr": "price_booster_dollar_fee",
                    "storage": [
                        "order"
                    ],
                    "format": ".2f",
                    "before_value": "(",
                    "after_value": "$)"
                }
            ],
            "markdown_name": "<b>",
            "markdown_value": None,
            "separator": " "
        }
    ],
    "separator": "<br>▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬<br>",
    "separator_field": "<br>"
}
OrderRenderResp = {
    "name": "resp",
    "fields": [
        {
            "name": "Booster",
            "fields": [
                {
                    "attr": "username",
                    "storage": [
                        "response"
                    ],
                    "format": None,
                    "before_value": "@",
                    "after_value": None
                }
            ],
            "markdown_name": "<b>",
            "markdown_value": None,
            "separator": " "
        },
        {
            "name": "Text",
            "fields": [
                {
                    "attr": "text",
                    "storage": [
                        "response", "extra"
                    ],
                    "format": None,
                    "before_value": None,
                    "after_value": None
                }
            ],
            "markdown_name": "<b>",
            "markdown_value": None,
            "separator": " "
        },
        {
            "name": "ETA",
            "fields": [
                {
                    "attr": "eta",
                    "storage": [
                        "response", "extra"
                    ],
                    "format": None,
                    "before_value": None,
                    "after_value": None
                }
            ],
            "markdown_name": "<b>",
            "markdown_value": None,
            "separator": " "
        },
        {
            "name": "Price",
            "fields": [
                {
                    "attr": "price",
                    "storage": [
                        "response", "extra"
                    ],
                    "format": ".2f",
                    "before_value": None,
                    "after_value": "р."
                }
            ],
            "markdown_name": "<b>",
            "markdown_value": None,
            "separator": " "
        },
        {
            "name": "Start Date",
            "fields": [
                {
                    "attr": "start_date",
                    "storage": [
                        "response", "extra"
                    ],
                    "format": None,
                    "before_value": None,
                    "after_value": None
                }
            ],
            "markdown_name": "<b>",
            "markdown_value": None,
            "separator": " "
        }
    ],
    "separator": "<br>▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬<br>",
    "separator_field": "<br>"
}

OrderRenderAdminResp = {
    "name": "resp-admin",
    "fields": [
        {
            "name": "Booster",
            "fields": [
                {
                    "attr": "username",
                    "storage": [
                        "response"
                    ],
                    "format": None,
                    "before_value": "@",
                    "after_value": None
                }
            ],
            "markdown_name": "<b>",
            "markdown_value": None,
            "separator": " "
        },
        {
            "name": "Text",
            "fields": [
                {
                    "attr": "text",
                    "storage": [
                        "response", "extra"
                    ],
                    "format": None,
                    "before_value": None,
                    "after_value": None
                }
            ],
            "markdown_name": "<b>",
            "markdown_value": None,
            "separator": " "
        },
        {
            "name": "ETA",
            "fields": [
                {
                    "attr": "eta",
                    "storage": [
                        "response", "extra"
                    ],
                    "format": None,
                    "before_value": None,
                    "after_value": None
                }
            ],
            "markdown_name": "<b>",
            "markdown_value": None,
            "separator": " "
        },
        {
            "name": "Price",
            "fields": [
                {
                    "attr": "price",
                    "storage": [
                        "response", "extra"
                    ],
                    "format": ".2f",
                    "before_value": None,
                    "after_value": "р."
                }
            ],
            "markdown_name": "<b>",
            "markdown_value": None,
            "separator": " "
        },
        {
            "name": "Start Date",
            "fields": [
                {
                    "attr": "start_date",
                    "storage": [
                        "response", "extra"
                    ],
                    "format": None,
                    "before_value": None,
                    "after_value": None
                }
            ],
            "markdown_name": "<b>",
            "markdown_value": None,
            "separator": " "
        },
        {
            "name": "Approved",
            "fields": [
                {
                    "attr": "approved",
                    "storage": [
                        "response"
                    ],
                    "format": None,
                    "before_value": None,
                    "after_value": None
                }
            ],
            "markdown_name": "<b>",
            "markdown_value": None,
            "separator": " "
        }
    ],

    "separator": "<br>▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬<br>",
    "separator_field": "<br>"
}

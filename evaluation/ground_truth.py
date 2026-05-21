GROUND_TRUTH_EMAILS = [

    {
        "input": {
            "subject": "Invoice #12345 - Payment Due",
            "body": "Please find attached invoice."
        },

        "expected": "invoice",
    },

    {
        "input": {
            "subject": "WIN FREE iPHONE NOW!!!",
            "body": "Click here to claim prize!"
        },

        "expected": "spam",
    },

    {
        "input": {
            "subject": "URGENT: Server Down",
            "body": "Production server is down."
        },

        "expected": "urgent",
    },

    {
        "input": "Can we schedule a meeting next week?",

        "expected": "general",
    },
]
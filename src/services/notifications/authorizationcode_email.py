from fastapi import FastAPI
from fastapi_mail import MessageSchema, MessageType, FastMail
from src.root.config.email_config import conf, get_base_email_styling
from src.models.email_model import EmailSchema
from jinja2 import Environment, FileSystemLoader

# load template
template_loader = Environment(loader=FileSystemLoader("./templates"))


async def send_email(
    email: EmailSchema,
    template_name: str,
    passcode: str,
    styling=get_base_email_styling,
):
    # template = template_loader.get_template(template_name)
    styling = styling()
    expiration_time = "5 mins"
    # html_content = template.render(styling=styling, passcode=passcode)
    html_body = f"""
        <!DOCTYPE html>
    <html>
    <head>
        <title>2FA Verification Code</title>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        {styling}
    </head>
    <body>
        <div class="container">
        <h1>Two Factor Authentication code</h1>
        <p>Your verification code is:</p>
        <div class="code">{passcode}</div>
        <p>This verification code will expire in {expiration_time}.</p>
        <p>
            Please enter this code into the application to reset your account
            password.
        </p>
        <p>If you did not request this code, please ignore this email.</p>
        </div>
    </body>
    </html>

    """
    message = MessageSchema(
        subject=email.subject,
        recipients=email.recipients,
        # template_body={"styling": styling(), "passcode": passcode},
        body=html_body,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message)

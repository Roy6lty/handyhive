from fastapi_mail import ConnectionConfig
from src.root.env_settings import env

conf = ConnectionConfig(
    MAIL_USERNAME=env.MAIL_USERNAME,
    MAIL_PASSWORD=env.MAIL_PASSWORD,
    MAIL_PORT=env.MAIL_PORT,
    MAIL_FROM=env.MAIL_FROM,
    MAIL_SERVER=env.MAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    TEMPLATE_FOLDER="./templates",
)  # pyright: ignore[reportCallIssue]


def get_base_email_styling() -> str:
    return """
    <style>
        body {
          font-family: sans-serif;
          margin: 0;
          padding: 0;
          background-color: #f4f4f4;
        }

        .container {
          max-width: 600px;
          margin: 50px auto;
          padding: 30px;
          background-color: #ffffff;
          box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
          border-radius: 5px;
        }

        h1 {
          color: #333333;
          text-align: center;
          margin-bottom: 20px;
        }

        p {
          color: #555555;
          line-height: 1.6;
          margin-bottom: 15px;
        }

        .code {
          background-color: #f0f0f0;
          padding: 15px;
          font-size: 24px;
          font-weight: bold;
          text-align: center;
          border-radius: 5px;
          margin-bottom: 20px;
        }
      </style>
      """

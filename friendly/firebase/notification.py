from firebase_admin import messaging


def send_fcm_notification(device_token: str, title: str, body: str):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=device_token,
    )

    # Send the notification
    response = messaging.send(message)
    print(f"Successfully sent message: {response}")


# Example usage
send_fcm_notification(device_token="", title="Hello!", body="You have a new notification.")

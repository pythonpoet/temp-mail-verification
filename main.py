from tempmail import EMail

email = EMail()
print(email.address)  # qwerty123@1secmail.com


# ... request some email ...

msg = email.wait_for_message()
print(msg.body)  # Hello World!\n
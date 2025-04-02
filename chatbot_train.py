from chatterbot.trainers import ListTrainer

custom_faqs = [
    ["Hi", "Hello! How can I assist you today?"],
    ["What services do you offer?", "We provide 24/7 customer support, order tracking, and technical assistance."],
    ["How can I track my order?", "You can track your order by logging into your account and checking the 'Order Status' section."],
    ["What are your working hours?", "Our customer support is available 24/7 to assist you."],
    ["How do I reset my password?", "Click on 'Forgot Password' on the login page and follow the instructions."],
    ["Can I cancel my order?", "Yes, you can cancel your order within 24 hours of purchase from your account settings."],
    ["Do you offer refunds?", "Yes, refunds are processed within 5-7 business days after cancellation."],
    ["Thank you", "You're welcome! Let me know if you need any further assistance."]
]

trainer = ListTrainer(chatbot)
for faq in custom_faqs:
    trainer.train(faq)

print("Custom FAQs Training Completed!")
 
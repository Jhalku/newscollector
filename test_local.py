import local_report_helper

print("Testing local report generation...")
articles = [
    {'title': 'Test Article 1', 'date': 'Yesterday', 'link': 'http://example.com/1'},
    {'title': 'Test Article 2', 'date': 'Today', 'link': 'http://example.com/2'}
]

res = local_report_helper.generate_news_report('Test Search', articles)
if res:
    print(f"Success! Report saved to {res}")
else:
    print("Failed")

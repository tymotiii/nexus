def run():
  test = yield (0x01, "Hello from init!")
  yield
  yield (0x13, f"test: {test}")

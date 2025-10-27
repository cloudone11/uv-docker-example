from fastapi import FastAPI
app = FastAPI()


def hello():
    print("Hello world3")


@app.get("/")
async def root():
    hello()
    return "Hello world6"

from fastapi import FastAPI, UploadFile, File, Response

app = FastAPI(title="Simple Image Storage API")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/upload/")
async def upload_file(file: UploadFile):
    with open(file.filename, "wb") as f:
        f.write(await file.read())
    # return {"file": file.filename}
    return Response(status_code=200)

import uvicorn


def main():

    uvicorn.run(

        app="src.app:app",
        host="0.0.0.0",
        workers=4,
    )
if __name__ == "__main__":
    main()
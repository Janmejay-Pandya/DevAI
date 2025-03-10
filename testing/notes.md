### To Create a new GitHub Repo

`{
  "command": "gh repo create my-new-repo --private --source=. --push",
  "description": "Creating a new GitHub repository"
}`

### To get folders and file structure in Linux
`tree -I "venv"`


### To make api request to Groq
`
client = Groq()

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": user_request,
        }
    ],
    model="llama3-8b-8192",
)

print(chat_completion.choices[0].message.content)
`

### To start remote vs-code (code-server)
`docker run -p 8080:8080 -v $(pwd)/code-environment:/tmp/code-environment code-server-update`

queryAgent = Agent(
    model='gemini-2.5-flash',
    name='queryAgent',
    description='A Agent that generates a SQL query from the given prompt.',
    instruction=""" Generate a SQL query based on the user prompt.""",
)

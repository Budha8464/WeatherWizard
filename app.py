# # Function Calling with OpenAI APIs
import requests
import os
import json
from dotenv import load_dotenv
import streamlit as st
load_dotenv()

from groq import Groq

# client = Groq(
#     api_key=os.getenv("GROQ_API_KEY"),
# )

# st.title("Weather App with Chat Interface")

# input_text = st.text_input("Hi, I am a weather chatbot. Ask me anything!")

# if st.button("Ask me"):
#     if not input_text:
#         st.error("Please enter a location!")

# ### Define Dummy Function

# Defines a dummy function to get the current weather
def get_current_weather(location):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={os.getenv("OPENWEATHER_API_KEY")}'
    response = requests.get(url)
    data=response.json()
    if data['cod'] == 200:
        return data
    else:
        return json.dumps({"city": location, "weather": "Data Fetch Error", "temperature": "N/A"})

# print(get_current_weather("London"))
# ### Define Functions
# 
# As demonstrated in the OpenAI documentation, here is a simple example of how to define the functions that are going to be part of the request. 
# 
# The descriptions are important because these are passed directly to the LLM and the LLM will use the description to determine whether to use the functions or how to use/call.



# # define a function as tools
# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_current_weather",
#             "description": "Get the current weather in a given location",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "location": {
#                         "type": "string",
#                         "description": "The city and state, e.g. San Francisco, CA"
#                     }
#                 },
#                 "required": ["location"]
#             }
#         }
#     },
# ]


def get_response(input_text,client):
    
    tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the real time weather of a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city, state and country, e.g. San Francisco, CA, US"
                    }
                },
                "required": ["location"]
            }
        }
    },
]
    response = client.chat.completions.create(
      model="mixtral-8x7b-32768",
        messages=[
          {
            "role": "system",
            "content": "You are a helpful assistant. You will asked details regarding the weather. If there is no question with respect to a weather, show a polite error message."
        },
        {
            "role": "user",
            "content": input_text+" Use a tool given to you",
             }
        ],
        temperature=0,
        max_tokens=300,
        tools=tools,
        tool_choice="auto"
    )
    # print(response)
    # print(response.choices[0].message.content)

    # print(response['choices'][0]['message']['tool_calls'][0]['function']['arguments'])

    groq_response = response.choices[0].message
    if groq_response is None:
        return "No response from Groq"
    else:
        groq_response = response.choices[0].message
        args = json.loads(groq_response.tool_calls[0].function.arguments)
    #    print(args)

        output=get_current_weather(**args)
    # print(groq_response)


    # response.tool_calls[0].function.arguments

    # We can now capture the arguments:



    # print(output)
    from groq import Groq

    client = Groq()
    completion = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant. You are given the weather details in json format. Read the data and then answer the question. Use a professional but fun tone when you say, and answer the question. All temperatures are in kelvin. Only mention details about the weather. If the JSON mentions data fetch error, only give a polite error message and tell the user to ask questions related to the weather of a place. "
        },
        {
            "role": "user",
            "content": json.dumps(output)+ "input_text"
        }
    ],
    temperature=0.4,
    max_tokens=300,
    top_p=1,
    stream=True,
    stop=None,
    )
    output=""
    # st.write("Response:")
    for chunk in completion:
        output+=chunk.choices[0].delta.content or ""
    # output+="\n"
    return output

def main():
    st.title("WeatherWizard")
    st.caption("Ask about any location's weather in plain English, get answers faster than you can say umbrella")
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY"),
        )
    # User input
    # st.write("Hi, I am a weather chatbot. Ask me anything!")
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
        
    # input_text = st.text_input("Type in your question")

    # Ask me button
    if prompt := st.chat_input():
    

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        response = get_response(prompt,client)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
if __name__ == "__main__":
    main()

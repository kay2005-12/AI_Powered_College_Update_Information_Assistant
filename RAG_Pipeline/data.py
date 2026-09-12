import os
from dotenv import load_dotenv
from langsmith import Client

# Load environment variables from .env file
load_dotenv()

# Client will automatically read LANGCHAIN_API_KEY from environment variables
client = Client()

dataset_name = "cemk-notices-evaluation"

# Create Evaluation Dataset
dataset = client.create_dataset(
    dataset_name=dataset_name,
    description="Evaluation dataset containing ground truth pairs from CEMK Notices.",
)

# Test cases derived from Cemk-Notices.csv
examples = [
    {
        "inputs": {"question": "When was the tender for Multifunction Laser Printer and High-Speed Document Scanner published?"},
        "outputs": {"ground_truth": "The tender was published on 2026-09-03 by the Dept of Central Administration."}
    },
    {
        "inputs": {"question": "Who was the Chief Guest at the inauguration of the CEMK Astronomy Club?"},
        "outputs": {"ground_truth": "Dr. Narayan Banerjee, Emeritus Professor at IIEST Shibpur, was the Chief Guest."}
    },
    {
        "inputs": {"question": "Who was the speaker for the Student Development Program on Specialized Coding held in January 2026?"},
        "outputs": {"ground_truth": "Mr. Alok Halder, CEO & MD of PCS Global Pvt. Limited, was the speaker."}
    },
    {
        "inputs": {"question": "When was the Blood Donation Camp for AY 2024-2025 organized by NSS and NCC Units?"},
        "outputs": {"ground_truth": "The Blood Donation Camp was organized on Saturday, May 3, 2025, from 10:00 AM to 3:00 PM."}
    },
    {
        "inputs": {"question": "Which organization conducted the Yoga Camp 2025 at CEMK on April 23, 2025?"},
        "outputs": {"ground_truth": "The Yoga Camp 2025 was organized by the NSS Unit of College of Engineering & Management, Kolaghat."}
    },
    {
        "inputs": {"question": "Where was the Thalassaemia test camp held on 25th September 2024?"},
        "outputs": {"ground_truth": "The Thalassaemia test camp was held at the TPO Conference Room."}
    },
    {
        "inputs": {"question": "Which department organized the Faculty Development Program ICTEA-2025?"},
        "outputs": {"ground_truth": "It was organized by the Department of Computer Science and Engineering."}
    },
    {
        "inputs": {"question": "What was the theme/topic of the Open Mic event organized on 10/9/2025?"},
        "outputs": {"ground_truth": "The event focus was Mental Health & Suicide Prevention, organized by the Mental Health Club."}
    },
    {
        "inputs": {"question": "What is the official name of the Annual Sports Meet held at CEMK on March 28, 2026?"},
        "outputs": {"ground_truth": "The Annual Sports Meet is named ATHLEEMA- 2026."}
    },
    {
        "inputs": {"question": "When was the notice for Admission in B.Tech through WBJEE Counselling 2026 published?"},
        "outputs": {"ground_truth": "The notice was published on 2026-07-07."}
    },
    {
        "inputs": {"question": "Which committee conducted the internal evaluation for Smart India Hackathon (SIH) 2026?"},
        "outputs": {"ground_truth": "The Technical Activities Committee (TAC) in association with the Institutions' Innovation Council (IIC)."}
    },
    {
        "inputs": {"question": "What was the venue for the online streaming session on ANRF Schemes & Opportunities on 31 July 2026?"},
        "outputs": {"ground_truth": "The event venue was the TPO Conference Room."}
    },
    {
        "inputs": {"question": "When was the Inter-College Hackathon organized by the Department of CSE held?"},
        "outputs": {"ground_truth": "The Inter-College Hackathon was held on 18th April 2026."}
    },
    {
        "inputs": {"question": "On which dates was the Quiz on Science & Technology organized by the NSS Unit?"},
        "outputs": {"ground_truth": "It was held on 28th February 2025 and 12th March 2025."}
    },
    {
        "inputs": {"question": "Where was the Entrepreneurship Idea Competition held on 7/11/2025?"},
        "outputs": {"ground_truth": "The competition was held at Venue W305 from 8:30 am to 11:30 am."}
    }
]

# Push Examples to LangSmith Dataset
client.create_examples(
    inputs=[e["inputs"] for e in examples],
    outputs=[e["outputs"] for e in examples],
    dataset_id=dataset.id,
)

print(f"Successfully uploaded {len(examples)} examples to dataset: '{dataset_name}'")
# Guardian Angel Presentation

---

## Slide 1: Title Slide

**Guardian Angel: A Real-Time Personal Safety Application**

*(Your Name/Team Name)*

---

## Slide 2: The Problem

In critical situations, every second counts. The challenge is to provide a personal safety tool that is not only fast and reliable but also versatile enough to handle different types of emergencies. Traditional methods can be slow or may not be accessible when they are needed most. We need a modern solution that empowers individuals to signal for help instantly and effectively.

---

## Slide 3: Our Solution: Guardian Angel

Guardian Angel is a proof-of-concept application designed to address this challenge. It provides a simple yet powerful platform for:

*   **User Simulation:** A safe environment to configure user profiles and emergency contacts.
*   **Live Alert Monitoring:** A centralized dashboard for observing and managing incoming distress signals in real-time.

Our goal is to demonstrate a robust system that can be the foundation for a comprehensive personal safety network.

---

## Slide 4: Key Features

*   **User Profiles:** Users can create and manage their profiles, including personal information, medical history, and a list of emergency contacts. This ensures that first responders and loved ones have the critical information they need.

*   **Immediate Panic Button:** A prominent panic button allows users to send an instant, high-priority alert with their location to all their emergency contacts.

*   **Detailed Alerts:** For situations where more context is needed, users can send alerts with custom text messages or by recording a voice message.

*   **Live Alert Monitor:** A real-time dashboard displays the 10 most recent incidents, allowing for immediate awareness and response.

---

## Slide 5: Technical Architecture

Guardian Angel is built on a modern, scalable tech stack:

*   **Frontend:** We used **Streamlit** to rapidly develop an interactive and user-friendly web interface.

*   **Backend:** The core of our application is a **FastAPI** server, which provides a high-performance, asynchronous API for handling alerts and managing data.

*   **Database:** **MongoDB** serves as our primary database, offering a flexible and scalable solution for storing user profiles and incident logs.

*   **Vector Database:** We have integrated **Milvus** to store vector embeddings of incident transcripts. This is a forward-looking feature that will enable powerful AI-driven capabilities, such as finding semantically similar past incidents to identify patterns.

---

## Slide 6: Development & Troubleshooting

During the development of this proof-of-concept, we successfully navigated several technical challenges:

*   **UI Modifications:** We tailored the user interface based on requirements, such as removing the "ambient listening" feature to streamline the user experience.

*   **Fixing Location Services:** We resolved issues with browser-based geolocation to ensure that accurate location data is captured and sent with every alert.

*   **Ensuring Data Integrity:** We debugged and fixed issues to ensure that user profiles and their emergency contacts are saved correctly and reliably in our MongoDB database.

*   **Correcting API Endpoints:** We identified and corrected a misconfigured API endpoint to ensure that the live alert monitor displays recent incidents as intended.

*   **Debugging Multi-Contact Notifications:** We are actively working on resolving an issue to ensure that email alerts are sent to all configured emergency contacts, not just the first one.

---

## Slide 7: Next Steps & Future Work

This proof-of-concept is just the beginning. Our roadmap for Guardian Angel includes:

*   **Resolve Client-Side Voice Recording:** We will continue to investigate and resolve the client-side WebRTC issues to ensure that the voice recording feature is robust across all browsers.

*   **Fully Implement Milvus Vector Search:** We plan to build out the functionality to perform semantic searches on past incidents, providing valuable insights for emergency responders.

*   **Expand Notification Options:** We will integrate additional notification channels, such as direct SMS (via services like Twilio) and WhatsApp, to provide more reliable and versatile alerting options.

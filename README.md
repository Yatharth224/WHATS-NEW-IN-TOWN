# 🏙️ What's New in Town

## Overview

**What's New in Town** is a city-based discovery platform that helps users explore **newly opened places** in their city.  
The platform reduces repetitive outings by offering structured discovery powered by an **AI-based review recommendation system** trained on **authentic Zomato customer reviews**.

---


###  Live Demo:  https://whatsnew-yatharthsingh.azurewebsites.net/

    
## 🚀 Key Features

- Discover **newly opened places** across major Indian cities
- AI-powered **review-based recommendations**
- Trained on **real customer reviews sourced from Zomato**
- Transparent, data-backed confidence scores
- Scalable and future-ready architecture

---

## 🏙️ Supported Cities

Currently available in:

- **Indore**
- **Mumbai**
- **Delhi**
- **Bengaluru**

---

## 🗂️ Categories

Users can explore new places under the following categories:

- **Fine Dine** – Newly opened fine dining restaurants
- **Restro Bar** – New restro bars and nightlife venues
- **Arcades** – Entertainment and gaming arcades
- **Bowling** – Newly launched bowling alleys

---

## 🤖 AI-Powered Review-Based Recommendation System

The core of **What's New in Town** is its **AI-driven recommendation engine**, which uses **semantic understanding of customer reviews** instead of traditional keyword-based matching.

### 📊 Data Source

- All restaurant **reviews are collected from Zomato**
- Restaurant metadata is sourced from **Zomato Collections**
- Only **real customer feedback and ratings** are used
- No manual bias or hardcoded rankings

---

## 🧠 Recommendation Engine – Technical Overview

The recommendation system is built using the **Sentence Transformers library** to perform semantic similarity matching between user queries and customer reviews.

### 🔄 Workflow

#### 1. Review Cleaning & Preprocessing
- All Zomato-sourced reviews are cleaned and normalized
- Noise such as emojis, special characters, extra spaces, and irrelevant tokens is removed
- Clean text ensures better embedding quality

#### 2. Sentence Embedding Generation
- Cleaned reviews are converted into **vector embeddings** using a Sentence Transformer model
- These embeddings capture **semantic meaning**, not just keywords
- All review embeddings are stored in a database for fast retrieval

#### 3. User Query Processing
- The user enters a search query (e.g., *best newly opened restro bar in Mumbai*)
- The query is converted into an embedding using the same transformer model

#### 4. Semantic Similarity Matching
- The query embedding is compared with stored review embeddings
- **Cosine similarity** is used to measure relevance
- Reviews with the highest similarity scores are identified

#### 5. Recommendation Generation
- Restaurants with the most relevant reviews are ranked
- The system returns the **Top 3 best-matched places**
- Each recommendation includes a **percentage confidence score** representing match accuracy

This approach enables **context-aware, accurate, and trustworthy recommendations** based on real customer experiences.

---

## 📍 Current AI Coverage

### Cities
- Indore
- Mumbai
- Bengaluru

### Categories
- Restro Bar
- Fine Dine

> Support for additional cities and categories will be added in future releases.

---

## 🧭 Application Flow

1. **User Enters a Query**
2. **AI Analyzes Zomato Reviews**
3. **Semantic Matching via Embeddings**
4. **Top 3 Recommendations Returned**
5. **Confidence Scores Displayed**
6. **User Discovers New Places with Confidence**

---

## ✅ Why What's New in Town?

- Uses **authentic Zomato-sourced reviews**
- AI-driven **review-based intelligence**
- No fake ratings or manual bias
- Semantic understanding of user intent
- Designed for scalability and future expansion

---

## 🔮 Future Enhancements

- Expansion to more cities
- Addition of new place categories
- Larger Zomato datasets for improved accuracy
- Advanced ranking and scoring algorithms
- Personalized recommendations based on user behavior
- Real-time data updates

---

### 🧩 Tech Stack

### Backend & AI
- **Python** – Core programming language
- **Flask** – Backend web framework
- **Sentence Transformers** – Semantic text embedding generation
- **Cosine Similarity** – Review and query relevance matching
- **Vector Database** – Efficient storage and retrieval of embeddings

### Data
- **Zomato Reviews (Scraped)** – Customer reviews scraped from Zomato and used to train the AI recommendation system
- **Zomato Collections (Scraped)** – Restaurant and category metadata scraped from Zomato Collections

### Frontend
- **HTML** – Page structure
- **CSS** – Styling and layout
- **JavaScript** – Client-side interactivity

### Others
- **JSON** – Data exchange format


## 📌 Conclusion

**What's New in Town** combines structured city discovery with a **Zomato-powered, review-based AI recommendation system**.  
By leveraging real customer reviews and semantic AI models, the platform delivers **reliable, transparent, and high-quality recommendations** for discovering new places.

---

⭐ If you find this project useful, feel free to **star the repository** and contribute!

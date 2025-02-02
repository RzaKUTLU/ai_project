from fastapi import FastAPI, HTTPException, Form, Request
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, status
import secrets
import os
from contextlib import asynccontextmanager

app = FastAPI()
security = HTTPBasic()

# AI Kategorileri için Enum
class Category(str, Enum):
    CODE = "Kod"
    GENERAL = "Genel Kullanım"
    VISUAL = "Görsel"
    ACADEMIC = "Akademik"  # Yeni kategori eklendi

# AI Model şeması
class AIModel(BaseModel):
    id: Optional[int]
    name: str
    image_url: str
    link_url: str
    description: str
    category: Category
    rating: float = 0.0  # Ortalama puan
    vote_count: int = 0  # Toplam oy sayısı

# Bunun yerine sadece dosya tabanlı sistemi kullanın
ai_models = [AIModel(**model) for model in [
    {
        "id": 1,
        "name": "ChatGPT",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/ChatGPT-Logo.svg/130px-ChatGPT-Logo.svg.png",
        "link_url": "https://chatgpt.com/",
        "description": "ChatGPT, OpenAI tarafından geliştirilen ve diyalog konusunda uzmanlaşmış bir yapay zeka sohbet botudur.",
        "category": "Genel Kullanım",
        "rating": 4.5,
        "vote_count": 2
    },
    {
        "id": 2,
        "name": "Claude",
        "image_url": "https://cdn.prod.website-files.com/667bba09c1fd0c0d87a8fe89/669b4b707124073bea61bbe4_Claude.svg",
        "link_url": "https://claude.ai",
        "description": "Claude AI, Anthropic tarafından geliştirilen bir üretken yapay zeka sohbet robotu ve büyük dil modelleri ailesidir.",
        "category": "Genel Kullanım",
        "rating": 4.7,
        "vote_count": 3
    },
    {
        "id": 3,
        "name": "DeepSeek",
        "image_url": "https://i.bstr.es/drivingeco/2025/01/Deepseek-r1-logo.webp",
        "link_url": "https://www.deepseek.com/",
        "description": "DeepSeek AI, Çin merkezli bir yapay zeka araştırma laboratuvarıdır ve özellikle yapay zeka tabanlı dil modelleri geliştirme alanında uzmanlaşmıştır.",
        "category": "Genel Kullanım",
        "rating": 5.0,
        "vote_count": 2
    },
    {
        "id": 4,
        "name": "Kimi AI",
        "image_url": "https://getcn.app/wp-content/uploads/2024/04/kimi-chat-app-icon.webp",
        "link_url": "https://kimi.moonshot.cn/",
        "description": "Kimi Chat, Beijing Moonshot Technology Co. Ltd tarafından geliştirilen tüm ihtiyaçlarınıza cevap veren ücretsiz bir AI sohbet botu ve araçtır.",
        "category": "Görsel",
        "rating": 0.0,
        "vote_count": 0
    },
    {
        "id": 5,
        "name": "İdeogram Aİ",
        "image_url": "https://www.webtures.com/wp-content/uploads/2024/12/Ideogram.png",
        "link_url": "https://ideogram.ai/login",
        "description": "İdeogram, gerçekçi görseller, posterler, logolar ve daha fazlasını üreten ücretsiz bir yapay zeka aracıdır.",
        "category": "Görsel",
        "rating": 4.0,
        "vote_count": 1
    },
    {
        "id": 6,
        "name": "Microsoft Copilot (AI Görüntü Oluşturucu)",
        "image_url": "https://images.indianexpress.com/2024/02/Microsoft-copilot.jpg",
        "link_url": "https://copilot.microsoft.com/images/create?FORM=GENEXP",
        "description": "Ücretsiz, yapay zeka destekli metinden görüntüye dönüştürücü, kelimelerinizi saniyeler içinde çarpıcı görsellere dönüştürür.",
        "category": "Görsel",
        "rating": 0.0,
        "vote_count": 0
    },
    {
        "id": 7,
        "name": "GitHub Copilot",
        "image_url": "https://cdn.prod.website-files.com/6344c9cef89d6f2270a38908/644158d0438c1513788efeb4_1366_2000.jpeg",
        "link_url": "https://github.com/features/copilot",
        "description": "GitHub Copilot, kullanıcıların kod yazma sürecinde yardımcı olan bulut tabanlı bir yapay zeka aracıdır.",
        "category": "Kod",
        "rating": 0.0,
        "vote_count": 0
    },
    {
        "id": 8,
        "name": "KLING AI",
        "image_url": "https://aitrends.com.tr/wp-content/uploads/2024/07/Kling-ai.webp",
        "link_url": "https://klingai.com/",
        "description": "KLING AI, son teknoloji jeneratif AI yöntemlerine dayalı, yaratıcı görseller ve videolar oluşturmaya yarayan araçlardır.",
        "category": "Görsel",
        "rating": 0.0,
        "vote_count": 0
    },
    {
        "id": 9,
        "name": "Image Creator in Bing",
        "image_url": "https://www.digitalmarketingcommunity.com/wp-content/uploads/2023/12/Featured-image-550-X-340-8-2.jpg",
        "link_url": "https://www.bing.com/images/create",
        "description": "Ücretsiz, yapay zeka destekli metinden görüntüye oluşturucu, kelimelerinizi saniyeler içinde çarpıcı görsellere dönüştürür.",
        "category": "Görsel",
        "rating": 4.0,
        "vote_count": 1
    },
    {
        "id": 10,
        "name": "Semantic Scholar",
        "image_url": "https://www.digitalmarketingcommunity.com/wp-content/uploads/2023/12/Featured-image-550-X-340-8-2.jpg",
        "link_url": "https://www.semanticscholar.org/",
        "description": "Semantic Scholar, yapay zeka destekli akademik arama motoru, bilimsel makaleleri analiz eder ve araştırmacılara önemli içgörüler sunar. Allen AI Institute tarafından geliştirilmiştir.",
        "category": "Akademik",
        "rating": 0.0,
        "vote_count": 0
    },
    {
        "id": 11,
        "name": "Elicit AI",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQyHrX6eLQJ6_AHCmYUX9p2Qw7FmHWHJZx0Gg&usqp=CAU",
        "link_url": "https://elicit.org/",
        "description": "Elicit, araştırma sürecinizi hızlandırmak için yapay zeka kullanır. Akademik makaleleri analiz eder, özetler çıkarır ve araştırma sorularınızı yanıtlar.",
        "category": "Akademik",
        "rating": 0.0,
        "vote_count": 0
    }
]]

# CORS ayarlarını güncelle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Şifreyi çevre değişkeninden al
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "1111")

# Admin şifre kontrolü için fonksiyon
def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    try:
        correct_password = ADMIN_PASSWORD
        is_correct_password = secrets.compare_digest(
            credentials.password,
            correct_password
        )
        
        if not is_correct_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Yanlış şifre",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kimlik doğrulama hatası",
            headers={"WWW-Authenticate": "Basic"},
        )

# API endpoint'leri
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Ar-Ge AI Models Koleksiyonu</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                    text-align: center;
                }
                .models-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 20px;
                    margin-top: 30px;
                }
                .model-card {
                    background: white;
                    border-radius: 8px;
                    padding: 15px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                    position: relative;
                }
                .model-card:hover {
                    transform: translateY(-5px);
                }
                .model-card img {
                    width: 100%;
                    height: 150px;
                    object-fit: contain;
                    border-radius: 4px;
                }
                .model-card h3 {
                    margin: 10px 0;
                    color: #333;
                }
                .model-card p {
                    color: #666;
                    font-size: 0.9em;
                }
                .category-filter {
                    display: flex;
                    gap: 10px;
                    margin: 20px 0;
                    justify-content: center;
                }
                .category-btn {
                    padding: 8px 16px;
                    border: none;
                    border-radius: 4px;
                    background-color: #007bff;
                    color: white;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                .category-btn:hover {
                    background-color: #0056b3;
                    transform: translateY(-2px);
                }
                .category-btn.active {
                    background-color: #28a745;
                }
                .search-box {
                    width: 100%;
                    padding: 10px;
                    margin: 20px 0;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                .add-button {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background-color: #2ecc71;
                    color: white;
                    padding: 15px 25px;
                    border-radius: 30px;
                    text-decoration: none;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    font-weight: bold;
                    z-index: 1000;
                }
                .add-button:hover {
                    background-color: #27ae60;
                }
                .admin-actions {
                    display: none;
                    margin-top: 10px;
                    gap: 10px;
                }
                .edit-btn, .delete-btn {
                    padding: 5px 10px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    color: white;
                }
                .edit-btn {
                    background-color: #ffc107;
                }
                .delete-btn {
                    background-color: #dc3545;
                }
                .admin-mode .admin-actions {
                    display: flex;
                }
                .rating-container {
                    position: absolute;
                    bottom: 10px;
                    right: 10px;
                    display: flex;
                    align-items: center;
                    gap: 5px;
                }
                .star {
                    color: #ffd700;
                    cursor: pointer;
                    font-size: 20px;
                }
                .star:hover {
                    transform: scale(1.2);
                }
                .rating-text {
                    font-size: 14px;
                    color: #666;
                }
                .rank-badge {
                    position: absolute;
                    top: 10px;
                    left: 10px;
                    background-color: #ffd700;
                    color: #000;
                    width: 30px;
                    height: 30px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    font-size: 16px;
                }
                .reset-btn {
                    background-color: #dc3545;
                    margin-left: 10px;
                }
                .reset-btn:hover {
                    background-color: #c82333;
                }
                .site-title {
                    text-align: center;
                    margin-bottom: 10px;
                }
                .site-subtitle {
                    text-align: center;
                    font-style: italic;
                    color: #666;
                    margin-bottom: 30px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="site-title">🤖 Ar-Ge AI Models Koleksiyonu</h1>
                <p class="site-subtitle">Hayal et, tasarla ve hayata geçir</p>
                
                <div class="admin-controls">
                    <button onclick="toggleAdminMode()" class="category-btn">Admin Modu</button>
                    <button onclick="resetRatings()" class="category-btn reset-btn" style="display: none;">Puanları Sıfırla</button>
                </div>

                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="Model ara..." oninput="filterModels()">
                </div>

                <div class="category-filter">
                    <button class="category-btn active" onclick="filterByCategory('all')">Tümü</button>
                    <button class="category-btn" onclick="filterByCategory('Kod')">Kod</button>
                    <button class="category-btn" onclick="filterByCategory('Genel Kullanım')">Genel Kullanım</button>
                    <button class="category-btn" onclick="filterByCategory('Görsel')">Görsel</button>
                    <button class="category-btn" onclick="filterByCategory('Akademik')">Akademik</button>
                </div>

                <div class="models-grid" id="modelsGrid">
                    <!-- Modeller JavaScript ile buraya yüklenecek -->
                </div>
            </div>

            <a href="/add" class="add-button">+ Yeni Model Ekle</a>

            <script>
                let isAdminMode = false;

                async function toggleAdminMode() {
                    if (!isAdminMode) {
                        const password = prompt('Admin şifresini girin:');
                        if (password === '1111') {
                            isAdminMode = true;
                            document.body.classList.add('admin-mode');
                            document.querySelector('.reset-btn').style.display = 'inline-block';
                            loadModels();
                        } else {
                            alert('Yanlış şifre!');
                        }
                    } else {
                        isAdminMode = false;
                        document.body.classList.remove('admin-mode');
                        document.querySelector('.reset-btn').style.display = 'none';
                        loadModels();
                    }
                }

                async function resetRatings() {
                    if (!isAdminMode) {
                        alert('Puanları sıfırlamak için admin modunda olmalısınız!');
                        return;
                    }

                    if (confirm('Tüm puanları sıfırlamak istediğinizden emin misiniz? Bu işlem geri alınamaz!')) {
                        try {
                            const response = await fetch('/api/reset-ratings', {
                                method: 'POST'
                            });

                            if (response.ok) {
                                const result = await response.json();
                                if (result.success) {
                                    alert('Tüm puanlar başarıyla sıfırlandı!');
                                    loadModels();
                                } else {
                                    alert('Sıfırlama işlemi başarısız oldu!');
                                }
                            } else {
                                alert('Sıfırlama işlemi sırasında bir hata oluştu!');
                            }
                        } catch (error) {
                            console.error('Sıfırlama hatası:', error);
                            alert('Sıfırlama işlemi sırasında bir hata oluştu!');
                        }
                    }
                }

                function editModel(id) {
                    if (!isAdminMode) {
                        alert('Düzenleme yapmak için admin modunda olmalısınız!');
                        return;
                    }
                    window.location.href = `/edit/${id}`;
                }

                async function deleteModel(id) {
                    if (!isAdminMode) {
                        alert('Silme işlemi için admin modunda olmalısınız!');
                        return;
                    }
                    if (confirm('Bu modeli silmek istediğinizden emin misiniz?')) {
                        try {
                            const password = prompt('Admin şifresini girin:');
                            if (!password) return;

                            // Base64 kodlaması için kullanıcı adı boş bırakılabilir
                            const credentials = btoa(`:${password}`);
                            
                            const response = await fetch(`/api/models/${id}`, {
                                method: 'DELETE',
                                headers: {
                                    'Authorization': `Basic ${credentials}`,
                                    'Accept': 'application/json'
                                },
                                credentials: 'include'
                            });
                            
                            if (response.status === 401) {
                                alert('Yanlış şifre!');
                                return;
                            }
                            
                            if (response.ok) {
                                alert('Model başarıyla silindi!');
                                loadModels();  // Listeyi yenile
                            } else {
                                const error = await response.json().catch(() => ({}));
                                alert(error.detail || 'Silme işlemi başarısız oldu!');
                            }
                        } catch (error) {
                            console.error('Silme hatası:', error);
                            alert('Silme işlemi sırasında bir hata oluştu!');
                        }
                    }
                }

                // Tüm modelleri yükle
                async function loadModels() {
                    const response = await fetch('/api/models');
                    const models = await response.json();
                    displayModels(models);
                }

                // Modelleri görüntüle (güncellendi)
                function displayModels(models) {
                    // Modelleri puana göre sırala
                    models.sort((a, b) => b.rating - a.rating);
                    
                    const grid = document.getElementById('modelsGrid');
                    grid.innerHTML = '';
                    
                    models.forEach((model, index) => {
                        const card = document.createElement('div');
                        card.className = 'model-card';
                        
                        // İlk 3 model için rozet ekle
                        const rankBadge = index < 3 ? `<div class="rank-badge">${index + 1}</div>` : '';
                        
                        card.innerHTML = `
                            ${rankBadge}
                            <img src="${model.image_url}" alt="${model.name}" onerror="this.src='https://via.placeholder.com/150'">
                            <h3>${model.name}</h3>
                            <p>${model.description}</p>
                            <p><strong>Kategori:</strong> ${model.category}</p>
                            <a href="${model.link_url}" target="_blank">Siteye Git →</a>
                            <div class="admin-actions">
                                <button class="edit-btn" onclick="editModel(${model.id})">Düzenle</button>
                                <button class="delete-btn" onclick="deleteModel(${model.id})">Sil</button>
                            </div>
                            <div class="rating-container">
                                ${generateStars(model.id, model.rating)}
                                <span class="rating-text">(${model.rating.toFixed(1)} / ${model.vote_count} oy)</span>
                            </div>
                        `;
                        grid.appendChild(card);
                    });
                    
                    // Yıldızları aktif hale getir
                    setupRatingListeners();
                }

                // Yıldızları oluştur
                function generateStars(modelId, rating) {
                    let stars = '';
                    for (let i = 1; i <= 5; i++) {
                        const starClass = i <= rating ? 'fas fa-star' : 'far fa-star';
                        stars += `<i class="star ${starClass}" data-rating="${i}" data-model="${modelId}"></i>`;
                    }
                    return stars;
                }

                // Yıldız puanlama işlevselliğini ekle
                function setupRatingListeners() {
                    document.querySelectorAll('.star').forEach(star => {
                        star.addEventListener('click', async function() {
                            const rating = parseInt(this.dataset.rating);
                            const modelId = this.dataset.model;
                            
                            try {
                                const response = await fetch(`/api/models/${modelId}/rate`, {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                    },
                                    body: JSON.stringify({ rating: rating })
                                });
                                
                                if (response.ok) {
                                    const result = await response.json();
                                    if (result.success) {
                                        loadModels(); // Modelleri yeniden yükle
                                    } else {
                                        alert('Puanlama işlemi başarısız oldu!');
                                    }
                                } else {
                                    const error = await response.json();
                                    alert(error.detail || 'Puanlama işlemi başarısız oldu!');
                                }
                            } catch (error) {
                                console.error('Puanlama hatası:', error);
                                alert('Puanlama sırasında bir hata oluştu!');
                            }
                        });
                    });
                }

                // Kategoriye göre filtrele
                async function filterByCategory(category) {
                    // Aktif buton stilini güncelle
                    document.querySelectorAll('.category-btn').forEach(btn => {
                        btn.classList.remove('active');
                        if (btn.textContent === category || (category === 'all' && btn.textContent === 'Tümü')) {
                            btn.classList.add('active');
                        }
                    });

                    if (category === 'all') {
                        loadModels();
                    } else {
                        const response = await fetch('/api/models');
                        const allModels = await response.json();
                        const filteredModels = allModels.filter(model => model.category === category);
                        displayModels(filteredModels);
                    }
                }

                // Arama fonksiyonu
                const searchBox = document.querySelector('.search-box');
                searchBox.addEventListener('input', async (e) => {
                    const query = e.target.value.toLowerCase();
                    if (query.length > 0) {
                        const response = await fetch('/api/models');
                        const allModels = await response.json();
                        const filteredModels = allModels.filter(model => 
                            model.name.toLowerCase().includes(query) || 
                            model.description.toLowerCase().includes(query)
                        );
                        displayModels(filteredModels);
                        
                        // Arama yaparken tüm kategori butonlarını inactive yap
                        document.querySelectorAll('.category-btn').forEach(btn => {
                            btn.classList.remove('active');
                        });
                    } else {
                        loadModels();
                        // Aramayı temizleyince "Tümü" butonunu active yap
                        document.querySelectorAll('.category-btn').forEach(btn => {
                            btn.classList.remove('active');
                            if (btn.textContent === 'Tümü') {
                                btn.classList.add('active');
                            }
                        });
                    }
                });

                // Sayfa yüklendiğinde modelleri göster
                loadModels();
            </script>
        </body>
    </html>
    """

@app.get("/api/models", response_model=List[AIModel])
async def get_all_models():
    try:
        return ai_models
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models/{category}", response_model=List[AIModel])
async def get_models_by_category(category: Category):
    return [model for model in ai_models if model.category == category]

@app.post("/api/models", response_model=AIModel)
async def add_model(model: AIModel):
    model.id = len(ai_models) + 1
    ai_models.append(model)
    return model

@app.get("/api/models/search/{query}", response_model=List[AIModel])
async def search_models(query: str):
    return [
        model for model in ai_models 
        if query.lower() in model.name.lower() or query.lower() in model.description.lower()
    ]

# Form için yeni endpoint'ler
@app.get("/add", response_class=HTMLResponse)
async def add_form():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Yeni AI Model Ekle</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .form-group {
                    margin-bottom: 15px;
                }
                label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                }
                input, select, textarea {
                    width: 100%;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    box-sizing: border-box;
                }
                textarea {
                    height: 100px;
                }
                button {
                    background-color: #007bff;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #0056b3;
                }
                .back-link {
                    display: inline-block;
                    margin-top: 20px;
                    color: #007bff;
                    text-decoration: none;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Yeni AI Model Ekle</h1>
                <form action="/submit-model" method="post">
                    <div class="form-group">
                        <label for="name">Model Adı:</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="image_url">Görsel URL:</label>
                        <input type="url" id="image_url" name="image_url" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="link_url">Bağlantı URL:</label>
                        <input type="url" id="link_url" name="link_url" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="description">Açıklama:</label>
                        <textarea id="description" name="description" required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="category">Kategori:</label>
                        <select id="category" name="category" required>
                            <option value="Kod">Kod</option>
                            <option value="Genel Kullanım">Genel Kullanım</option>
                            <option value="Görsel">Görsel</option>
                            <option value="Akademik">Akademik</option>
                        </select>
                    </div>
                    
                    <button type="submit">Model Ekle</button>
                </form>
                <a href="/" class="back-link">← Ana Sayfaya Dön</a>
            </div>
        </body>
    </html>
    """

@app.post("/submit-model")
async def submit_model(
    name: str = Form(...),
    image_url: str = Form(...),
    link_url: str = Form(...),
    description: str = Form(...),
    category: Category = Form(...)
):
    new_model = AIModel(
        id=len(ai_models) + 1,
        name=name,
        image_url=image_url,
        link_url=link_url,
        description=description,
        category=category
    )
    ai_models.append(new_model)
    return RedirectResponse(url="/", status_code=303)

# Silme endpoint'ini güncelle
@app.delete("/api/models/{model_id}")
async def delete_model(model_id: int, credentials: HTTPBasicCredentials = Depends(verify_admin)):
    try:
        global ai_models
        original_length = len(ai_models)
        ai_models = [model for model in ai_models if model.id != model_id]
        
        if len(ai_models) == original_length:
            raise HTTPException(status_code=404, detail="Model bulunamadı")
            
        # ID'leri yeniden düzenle
        for i, model in enumerate(ai_models, 1):
            model.id = i
            
        return {"success": True, "message": "Model başarıyla silindi"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Düzenleme sayfası
@app.get("/edit/{model_id}", response_class=HTMLResponse)
async def edit_form(model_id: int):
    try:
        # ID'yi integer'a çevir
        model_id = int(model_id)
        # Modeli bul
        model = next((m for m in ai_models if m.id == model_id), None)
        
        if model is None:
            raise HTTPException(status_code=404, detail="Model bulunamadı")
        
        return f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>AI Model Düzenle</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 12px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    }}
                    h1 {{
                        color: #2c3e50;
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .form-group {{
                        margin-bottom: 20px;
                    }}
                    label {{
                        display: block;
                        margin-bottom: 8px;
                        font-weight: bold;
                    }}
                    input, select, textarea {{
                        width: 100%;
                        padding: 8px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        box-sizing: border-box;
                    }}
                    textarea {{
                        height: 100px;
                    }}
                    button {{
                        background-color: #2ecc71;
                        color: white;
                        padding: 10px 20px;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        width: 100%;
                    }}
                    button:hover {{
                        background-color: #27ae60;
                    }}
                    .back-link {{
                        display: inline-block;
                        margin-top: 20px;
                        color: #3498db;
                        text-decoration: none;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>AI Model Düzenle</h1>
                    <form action="/update-model/{model_id}" method="post">
                        <div class="form-group">
                            <label for="name">Model Adı:</label>
                            <input type="text" id="name" name="name" value="{model.name}" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="image_url">Görsel URL:</label>
                            <input type="url" id="image_url" name="image_url" value="{model.image_url}" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="link_url">Bağlantı URL:</label>
                            <input type="url" id="link_url" name="link_url" value="{model.link_url}" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="description">Açıklama:</label>
                            <textarea id="description" name="description" required>{model.description}</textarea>
                        </div>
                        
                        <div class="form-group">
                            <label for="category">Kategori:</label>
                            <select id="category" name="category" required>
                                <option value="Kod" {"selected" if model.category == "Kod" else ""}>Kod</option>
                                <option value="Genel Kullanım" {"selected" if model.category == "Genel Kullanım" else ""}>Genel Kullanım</option>
                                <option value="Görsel" {"selected" if model.category == "Görsel" else ""}>Görsel</option>
                                <option value="Akademik" {"selected" if model.category == "Akademik" else ""}>Akademik</option>
                            </select>
                        </div>
                        
                        <button type="submit">Değişiklikleri Kaydet</button>
                    </form>
                    <a href="/" class="back-link">← Ana Sayfaya Dön</a>
                </div>
            </body>
        </html>
        """
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Güncelleme endpoint'i
@app.post("/update-model/{model_id}")
async def update_model(
    model_id: int,
    name: str = Form(...),
    image_url: str = Form(...),
    link_url: str = Form(...),
    description: str = Form(...),
    category: Category = Form(...)
):
    global ai_models  # global değişkeni kullanacağımızı belirtiyoruz
    
    # Modeli bul ve güncelle
    for i, model in enumerate(ai_models):
        if model.id == model_id:
            ai_models[i] = AIModel(
                id=model_id,
                name=name,
                image_url=image_url,
                link_url=link_url,
                description=description,
                category=category
            )
            break
    
    return RedirectResponse(url="/", status_code=303)

# Rating için yeni bir model oluştur
class RatingData(BaseModel):
    rating: int

@app.post("/api/models/{model_id}/rate")
async def rate_model(model_id: int, rating_data: RatingData):
    try:
        rating = rating_data.rating
        if rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Puan 1-5 arasında olmalıdır")
        
        for model in ai_models:
            if model.id == model_id:
                # Yeni puanı mevcut ortalamaya ekle
                total_points = (model.rating * model.vote_count) + rating
                model.vote_count += 1
                model.rating = round(total_points / model.vote_count, 1)
                return {"success": True, "new_rating": model.rating}
        
        raise HTTPException(status_code=404, detail="Model bulunamadı")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Puanları sıfırlama endpoint'i
@app.post("/api/reset-ratings")
async def reset_ratings():
    try:
        for model in ai_models:
            model.rating = 0.0
            model.vote_count = 0
        return {"success": True, "message": "Tüm puanlar sıfırlandı"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return HTMLResponse(
        f"""
        <html>
            <body>
                <h1>Hata: {exc.status_code}</h1>
                <p>{exc.detail}</p>
                <a href="/">Ana Sayfaya Dön</a>
            </body>
        </html>
        """,
        status_code=exc.status_code
    )

# startup event'ini değiştirin
@app.on_event("startup")
async def startup_event():
    pass  # Artık dosyadan yükleme yapmayacağız

# Modelleri kaydetme
def save_models():
    with open('models.json', 'w') as f:
        json.dump([model.dict() for model in ai_models], f)

# Modelleri yükleme
def load_models():
    try:
        with open('models.json', 'r') as f:
            return [AIModel(**m) for m in json.load(f)]
    except:
        return default_models

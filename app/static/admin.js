// 景点管理系统 JavaScript

let attractions = [];
let currentEditId = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadAttractions();
    setupEventListeners();
});

// 设置事件监听器
function setupEventListeners() {
    // 表单提交
    document.getElementById('attractionForm').addEventListener('submit', handleFormSubmit);
    
    // 文件拖拽上传
    const uploadArea = document.querySelector('.file-upload-area');
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    
    // 模态框点击外部关闭
    document.getElementById('attractionModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });
}

// 加载景点列表
async function loadAttractions() {
    try {
        showLoading();
        const response = await fetch('/api/attractions?page_size=100');
        const data = await response.json();
        
        if (response.ok) {
            attractions = data.items;
            renderAttractions(attractions);
        } else {
            showError('加载景点列表失败: ' + (data.detail || '未知错误'));
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
}

// 渲染景点列表
function renderAttractions(attractionList) {
    const container = document.getElementById('attractionsList');
    
    if (attractionList.length === 0) {
        container.innerHTML = '<div class="loading">暂无景点数据</div>';
        return;
    }
    
    const html = attractionList.map(attraction => `
        <div class="attraction-card">
            <div class="attraction-header">
                <h4 class="attraction-name">${attraction.name}</h4>
                <div class="attraction-actions">
                    <button class="btn btn-secondary" onclick="editAttraction(${attraction.id})">✏️ 编辑</button>
                    <button class="btn btn-danger" onclick="deleteAttraction(${attraction.id})">🗑️ 删除</button>
                </div>
            </div>
            
            <div class="attraction-meta">
                <span>📍 ${attraction.category}</span>
                <span>⭐ ${attraction.rating}</span>
                ${attraction.distance ? `<span>📏 ${attraction.distance}</span>` : ''}
                <span>${attraction.is_recommended ? '🔥 推荐' : '📝 普通'}</span>
            </div>
            
            ${attraction.description ? `<div class="attraction-description">${attraction.description}</div>` : ''}
            
            ${attraction.cover_image ? `<img src="${attraction.cover_image}" class="image-preview" alt="${attraction.name}">` : ''}
            
            <div style="margin-top: 10px; font-size: 12px; color: #999;">
                ${attraction.latitude && attraction.longitude ? 
                    `坐标: ${attraction.latitude}, ${attraction.longitude}` : 
                    '未设置坐标'
                }
                | 权重: ${attraction.sort_order}
                | 创建: ${new Date(attraction.created_at).toLocaleDateString()}
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

// 显示加载状态
function showLoading() {
    document.getElementById('attractionsList').innerHTML = '<div class="loading">正在加载...</div>';
}

// 显示错误信息
function showError(message) {
    const container = document.getElementById('attractionsList');
    container.innerHTML = `<div class="error">${message}</div>`;
}

// 显示成功信息
function showSuccess(message) {
    // 创建临时成功提示
    const successDiv = document.createElement('div');
    successDiv.className = 'success';
    successDiv.textContent = message;
    successDiv.style.position = 'fixed';
    successDiv.style.top = '20px';
    successDiv.style.right = '20px';
    successDiv.style.zIndex = '9999';
    
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        document.body.removeChild(successDiv);
    }, 3000);
}

// 显示添加模态框
function showAddModal() {
    currentEditId = null;
    document.getElementById('modalTitle').textContent = '添加景点';
    document.getElementById('attractionForm').reset();
    document.getElementById('attractionId').value = '';
    document.getElementById('imagePreview').style.display = 'none';
    document.getElementById('coverImage').value = '';
    document.getElementById('attractionModal').style.display = 'block';
}

// 编辑景点
function editAttraction(id) {
    const attraction = attractions.find(a => a.id === id);
    if (!attraction) return;
    
    currentEditId = id;
    document.getElementById('modalTitle').textContent = '编辑景点';
    
    // 填充表单数据
    document.getElementById('attractionId').value = attraction.id;
    document.getElementById('name').value = attraction.name;
    document.getElementById('category').value = attraction.category;
    document.getElementById('description').value = attraction.description || '';
    document.getElementById('latitude').value = attraction.latitude || '';
    document.getElementById('longitude').value = attraction.longitude || '';
    document.getElementById('rating').value = attraction.rating;
    document.getElementById('distance').value = attraction.distance || '';
    document.getElementById('sortOrder').value = attraction.sort_order;
    document.getElementById('isRecommended').checked = attraction.is_recommended;
    document.getElementById('coverImage').value = attraction.cover_image || '';
    
    // 显示现有图片
    if (attraction.cover_image) {
        const preview = document.getElementById('imagePreview');
        preview.src = attraction.cover_image;
        preview.style.display = 'block';
    } else {
        document.getElementById('imagePreview').style.display = 'none';
    }
    
    document.getElementById('attractionModal').style.display = 'block';
}

// 关闭模态框
function closeModal() {
    document.getElementById('attractionModal').style.display = 'none';
    currentEditId = null;
}

// 处理表单提交
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('name').value,
        category: document.getElementById('category').value,
        description: document.getElementById('description').value || null,
        latitude: parseFloat(document.getElementById('latitude').value) || null,
        longitude: parseFloat(document.getElementById('longitude').value) || null,
        rating: parseFloat(document.getElementById('rating').value),
        distance: document.getElementById('distance').value || null,
        sort_order: parseInt(document.getElementById('sortOrder').value),
        is_recommended: document.getElementById('isRecommended').checked,
        cover_image: document.getElementById('coverImage').value || null
    };
    
    try {
        let response;
        if (currentEditId) {
            // 更新景点
            response = await fetch(`/api/attractions/${currentEditId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
        } else {
            // 创建景点
            response = await fetch('/api/attractions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
        }
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess(currentEditId ? '景点更新成功！' : '景点创建成功！');
            closeModal();
            loadAttractions(); // 重新加载列表
        } else {
            showError('操作失败: ' + (result.detail || '未知错误'));
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
}

// 删除景点
async function deleteAttraction(id) {
    const attraction = attractions.find(a => a.id === id);
    if (!attraction) return;
    
    if (!confirm(`确定要删除景点"${attraction.name}"吗？此操作不可恢复。`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/attractions/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showSuccess('景点删除成功！');
            loadAttractions(); // 重新加载列表
        } else {
            const result = await response.json();
            showError('删除失败: ' + (result.detail || '未知错误'));
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
}

// 图片预览
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('imagePreview');
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
        
        // 上传图片
        uploadImage(input.files[0]);
    }
}

// 上传图片
async function uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/attractions/upload-image', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            document.getElementById('coverImage').value = result.file_path;
            showSuccess('图片上传成功！');
        } else {
            showError('图片上传失败: ' + (result.detail || '未知错误'));
        }
    } catch (error) {
        showError('图片上传错误: ' + error.message);
    }
}

// 拖拽上传处理
function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type.startsWith('image/')) {
        const input = document.getElementById('imageFile');
        input.files = files;
        previewImage(input);
    }
}

// 刷新景点列表
function refreshAttractions() {
    loadAttractions();
}

// 筛选景点
function filterAttractions() {
    const category = document.getElementById('categoryFilter').value;
    const recommendedOnly = document.getElementById('recommendedOnly').checked;
    
    let filtered = attractions;
    
    if (category) {
        filtered = filtered.filter(a => a.category === category);
    }
    
    if (recommendedOnly) {
        filtered = filtered.filter(a => a.is_recommended);
    }
    
    renderAttractions(filtered);
}

// 搜索景点
function searchAttractions() {
    const keyword = document.getElementById('searchInput').value.toLowerCase();
    
    if (!keyword) {
        filterAttractions();
        return;
    }
    
    const filtered = attractions.filter(a => 
        a.name.toLowerCase().includes(keyword) ||
        (a.description && a.description.toLowerCase().includes(keyword)) ||
        a.category.toLowerCase().includes(keyword)
    );
    
    renderAttractions(filtered);
}

// 导出数据
function exportData() {
    const dataStr = JSON.stringify(attractions, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `attractions_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    showSuccess('数据导出成功！');
}
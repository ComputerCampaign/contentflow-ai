// 导航功能
document.addEventListener('DOMContentLoaded', function() {
    // 移动端导航切换
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }
    
    // 平滑滚动到锚点
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // 添加代码复制功能
    addCopyButtons();
    
    // 添加API端点展开/折叠功能
    addToggleFeature();
});

// 滚动到指定章节
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// 添加代码复制功能
function addCopyButtons() {
    const codeBlocks = document.querySelectorAll('.code-example pre');
    
    codeBlocks.forEach(block => {
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.textContent = '复制';
        copyButton.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: #4f46e5;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        const container = block.parentElement;
        container.style.position = 'relative';
        container.appendChild(copyButton);
        
        // 鼠标悬停显示复制按钮
        container.addEventListener('mouseenter', () => {
            copyButton.style.opacity = '1';
        });
        
        container.addEventListener('mouseleave', () => {
            copyButton.style.opacity = '0';
        });
        
        // 复制功能
        copyButton.addEventListener('click', async () => {
            const code = block.textContent;
            try {
                await navigator.clipboard.writeText(code);
                copyButton.textContent = '已复制';
                copyButton.style.background = '#10b981';
                
                setTimeout(() => {
                    copyButton.textContent = '复制';
                    copyButton.style.background = '#4f46e5';
                }, 2000);
            } catch (err) {
                console.error('复制失败:', err);
                copyButton.textContent = '复制失败';
                copyButton.style.background = '#ef4444';
                
                setTimeout(() => {
                    copyButton.textContent = '复制';
                    copyButton.style.background = '#4f46e5';
                }, 2000);
            }
        });
    });
}

// 添加API端点展开/折叠功能
function addToggleFeature() {
    const endpoints = document.querySelectorAll('.api-endpoint');
    
    endpoints.forEach(endpoint => {
        const header = endpoint.querySelector('.endpoint-header');
        const content = endpoint.querySelector('.endpoint-content');
        
        if (header && content) {
            // 添加展开/折叠图标
            const toggleIcon = document.createElement('span');
            toggleIcon.className = 'toggle-icon';
            toggleIcon.innerHTML = '▼';
            toggleIcon.style.cssText = `
                margin-left: auto;
                cursor: pointer;
                transition: transform 0.3s ease;
                font-size: 12px;
                color: #718096;
            `;
            
            header.appendChild(toggleIcon);
            header.style.cursor = 'pointer';
            
            // 点击切换展开/折叠
            header.addEventListener('click', () => {
                const isExpanded = content.style.display !== 'none';
                
                if (isExpanded) {
                    content.style.display = 'none';
                    toggleIcon.style.transform = 'rotate(-90deg)';
                    toggleIcon.innerHTML = '▶';
                } else {
                    content.style.display = 'block';
                    toggleIcon.style.transform = 'rotate(0deg)';
                    toggleIcon.innerHTML = '▼';
                }
            });
        }
    });
}

// 添加滚动监听，实现导航高亮
window.addEventListener('scroll', function() {
    const sections = document.querySelectorAll('.section');
    const navLinks = document.querySelectorAll('.nav-menu a');
    
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (pageYOffset >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#' + current) {
            link.classList.add('active');
            link.style.background = 'rgba(255,255,255,0.3)';
        } else {
            link.style.background = '';
        }
    });
});

// 添加搜索功能
function addSearchFeature() {
    const searchContainer = document.createElement('div');
    searchContainer.className = 'search-container';
    searchContainer.innerHTML = `
        <input type="text" id="apiSearch" placeholder="搜索API接口..." style="
            width: 100%;
            padding: 10px;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-size: 14px;
            margin-bottom: 20px;
        ">
    `;
    
    const mainContent = document.querySelector('.main-content');
    const firstSection = mainContent.querySelector('.section');
    mainContent.insertBefore(searchContainer, firstSection);
    
    const searchInput = document.getElementById('apiSearch');
    const endpoints = document.querySelectorAll('.api-endpoint');
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        
        endpoints.forEach(endpoint => {
            const header = endpoint.querySelector('.endpoint-header');
            const path = header.querySelector('.path').textContent.toLowerCase();
            const description = header.querySelector('.description').textContent.toLowerCase();
            const method = header.querySelector('.method').textContent.toLowerCase();
            
            const matches = path.includes(searchTerm) || 
                          description.includes(searchTerm) || 
                          method.includes(searchTerm);
            
            if (matches || searchTerm === '') {
                endpoint.style.display = 'block';
            } else {
                endpoint.style.display = 'none';
            }
        });
    });
}

// 添加页面加载动画
window.addEventListener('load', function() {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease-in-out';
    
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);
    
    // 添加卡片动画
    const cards = document.querySelectorAll('.category-card, .info-card, .permission-card, .api-endpoint');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s ease-out';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 + index * 50);
    });
    
    // 初始化搜索功能
    addSearchFeature();
});

// 添加键盘快捷键
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K 打开搜索
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('apiSearch');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // ESC 清空搜索
    if (e.key === 'Escape') {
        const searchInput = document.getElementById('apiSearch');
        if (searchInput && document.activeElement === searchInput) {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
            searchInput.blur();
        }
    }
});

// 添加返回顶部按钮
function addBackToTopButton() {
    const backToTop = document.createElement('button');
    backToTop.innerHTML = '↑';
    backToTop.className = 'back-to-top';
    backToTop.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        background: #4f46e5;
        color: white;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        font-size: 20px;
        opacity: 0;
        transition: all 0.3s ease;
        z-index: 1000;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    `;
    
    document.body.appendChild(backToTop);
    
    // 滚动显示/隐藏按钮
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTop.style.opacity = '1';
            backToTop.style.transform = 'scale(1)';
        } else {
            backToTop.style.opacity = '0';
            backToTop.style.transform = 'scale(0.8)';
        }
    });
    
    // 点击返回顶部
    backToTop.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// 初始化返回顶部按钮
document.addEventListener('DOMContentLoaded', addBackToTopButton);

// 添加打印样式优化
window.addEventListener('beforeprint', function() {
    // 展开所有折叠的内容
    const contents = document.querySelectorAll('.endpoint-content');
    contents.forEach(content => {
        content.style.display = 'block';
    });
    
    // 隐藏复制按钮
    const copyButtons = document.querySelectorAll('.copy-button');
    copyButtons.forEach(button => {
        button.style.display = 'none';
    });
});

window.addEventListener('afterprint', function() {
    // 恢复复制按钮
    const copyButtons = document.querySelectorAll('.copy-button');
    copyButtons.forEach(button => {
        button.style.display = 'block';
    });
});
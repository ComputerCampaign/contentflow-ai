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
    
    // 初始化性能图表
    initPerformanceChart();
    
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

// 初始化性能图表
function initPerformanceChart() {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;
    
    const performanceChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['响应时间', '并发处理', '扩展性', '可用性', '安全性', '维护性'],
            datasets: [{
                label: '当前架构',
                data: [85, 90, 95, 92, 88, 90],
                backgroundColor: 'rgba(102, 126, 234, 0.2)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(102, 126, 234, 1)'
            }, {
                label: '目标架构',
                data: [95, 95, 98, 96, 94, 95],
                backgroundColor: 'rgba(118, 75, 162, 0.2)',
                borderColor: 'rgba(118, 75, 162, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(118, 75, 162, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(118, 75, 162, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 1.5,
            plugins: {
                title: {
                    display: true,
                    text: '系统性能指标对比',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    min: 0,
                    ticks: {
                        stepSize: 20,
                        font: {
                            size: 12
                        }
                    },
                    pointLabels: {
                        font: {
                            size: 13,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    angleLines: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            elements: {
                line: {
                    borderWidth: 3
                },
                point: {
                    radius: 5,
                    hoverRadius: 8
                }
            },
            interaction: {
                intersect: false,
                mode: 'point'
            }
        }
    });
}

// 滚动到参考资料
function scrollToReference(refNumber) {
    const referencesSection = document.getElementById('references');
    if (referencesSection) {
        referencesSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
        
        // 高亮对应的参考文献
        setTimeout(() => {
            const referenceItems = document.querySelectorAll('.reference-item');
            referenceItems.forEach((item, index) => {
                if (index === refNumber - 1) {
                    item.style.backgroundColor = '#e6f3ff';
                    item.style.transform = 'scale(1.02)';
                    setTimeout(() => {
                        item.style.backgroundColor = '#f7fafc';
                        item.style.transform = 'scale(1)';
                    }, 2000);
                }
            });
        }, 500);
    }
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
        }
    });
});

// 添加页面加载动画
window.addEventListener('load', function() {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease-in-out';
    
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);
    
    // 添加卡片动画
    const cards = document.querySelectorAll('.principle-card, .service-card, .workflow-card, .tech-category');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s ease-out';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 + index * 50);
    });
});

// 添加图片懒加载
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                
                // 检查图片是否已经加载
                if (img.complete && img.naturalHeight !== 0) {
                    // 图片已加载，确保可见
                    img.style.opacity = '1';
                } else {
                    // 图片未加载，设置加载状态
                    img.style.opacity = '0';
                    img.style.transition = 'opacity 0.5s ease';
                    
                    img.onload = function() {
                        this.style.opacity = '1';
                    };
                    
                    img.onerror = function() {
                        this.style.opacity = '0.5';
                        this.style.filter = 'grayscale(100%)';
                        console.warn('图片加载失败:', this.src);
                    };
                }
                
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => {
        imageObserver.observe(img);
    });
});

// 添加打印样式优化
window.addEventListener('beforeprint', function() {
    // 展开所有折叠的内容
    const navMenu = document.getElementById('navMenu');
    if (navMenu) {
        navMenu.style.display = 'block';
    }
});

window.addEventListener('afterprint', function() {
    // 恢复原始状态
    const navMenu = document.getElementById('navMenu');
    const navToggle = document.getElementById('navToggle');
    if (navMenu && navToggle && !navToggle.classList.contains('active')) {
        navMenu.style.display = '';
    }
});
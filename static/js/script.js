document.addEventListener('DOMContentLoaded', function () {
    // --- ОБЩИЕ КОМПОНЕНТЫ (для всех страниц) ---

    // 1. Логика мобильной навигации и dropdown
    const navbarToggle = document.getElementById('navbarToggle');
    const navbarCollapse = document.getElementById('navbarNav');
    const navbar = document.querySelector('.navbar');

    if (navbarToggle && navbarCollapse && navbar) {
        navbarToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            navbarCollapse.classList.toggle('show');
        });

        document.addEventListener('click', function (e) {
            if (navbarCollapse.classList.contains('show') && !navbar.contains(e.target)) {
                navbarCollapse.classList.remove('show');
            }
        });

        navbarCollapse.querySelectorAll('a:not(.dropdown-toggle)').forEach(link => {
            link.addEventListener('click', () => {
                if (navbarCollapse.classList.contains('show')) {
                    navbarCollapse.classList.remove('show');
                }
            });
        });

        const dropdownToggle = document.querySelector('.nav-item.dropdown .nav-link.dropdown-toggle');
        if (dropdownToggle) {
            dropdownToggle.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                this.parentElement.classList.toggle('show');
            });
        }
    }

    // 2. Закрытие flash-сообщений (alerts)
    document.querySelectorAll('.alert-dismissible .btn-close').forEach(function (btn) {
        btn.addEventListener('click', function () {
            this.closest('.alert').remove();
        });
    });

    // 3. Универсальная логика для переключения вкладок (табов)
    const allTabs = document.querySelectorAll('.tabs .tab');
    if (allTabs.length > 0) {
        allTabs.forEach(function (tab) {
            tab.addEventListener('click', function () {
                const targetId = this.getAttribute('data-tab');
                // Ищем следующий элемент-контейнер для контента
                let tabContentWrapper = this.closest('.tabs').nextElementSibling;
                // Если следующий элемент не является оберткой, ищем внутри родителя
                if (!tabContentWrapper || !tabContentWrapper.querySelector('.tab-content')) {
                    tabContentWrapper = this.closest('.content-wrapper') || document; // Нужен общий родитель
                }

                const contentPanes = tabContentWrapper.querySelectorAll('.tab-content');
                
                // Убираем active со всех вкладок и панелей в их группе
                this.parentElement.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                contentPanes.forEach(c => c.classList.remove('active'));

                // Активируем нужную вкладку и панель
                this.classList.add('active');
                const targetPane = document.getElementById(targetId) || document.getElementById('tab-' + targetId);
                if(targetPane) {
                    targetPane.classList.add('active');
                }
            });
        });
    }

    // --- ЛОГИКА ДЛЯ КОНКРЕТНЫХ СТРАНИЦ ---

    // 4. Логика для страницы каталога (index.html)
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        const genreFilter = document.getElementById('genreFilter');
        const statusFilter = document.getElementById('statusFilter');
        const searchBtn = document.getElementById('searchBtn');

        const applyFilters = () => {
            const params = new URLSearchParams();
            if (searchInput.value) params.append('search', searchInput.value);
            if (genreFilter.value) params.append('genre', genreFilter.value);
            if (statusFilter.value) params.append('status', statusFilter.value);
            window.location.href = '/?' + params.toString();
        };

        if (searchBtn) searchBtn.addEventListener('click', applyFilters);
        if (searchInput) searchInput.addEventListener('keyup', (e) => e.key === 'Enter' && applyFilters());
        if (genreFilter) genreFilter.addEventListener('change', applyFilters);
        if (statusFilter) statusFilter.addEventListener('change', applyFilters);
    }

    // 5. Логика бронирования книг (index.html)
    const reserveButtons = document.querySelectorAll('.reserve-btn');
    if (reserveButtons.length > 0) {
        reserveButtons.forEach(button => {
            button.addEventListener('click', function () {
                const bookId = this.getAttribute('data-book-id');
                fetch('/api/reserve', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ book_id: bookId })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Ошибка: ' + data.message);
                    }
                })
                .catch(err => console.error('Ошибка бронирования:', err));
            });
        });
    }


    // 6. Логика для админ-панели (admin.html)
    const adminUsersTab = document.querySelector('.tab[data-tab="users"]');
    if (adminUsersTab) {
        // Логика активации таба из URL (для перезагрузки страницы после действий)
        const urlParams = new URLSearchParams(window.location.search);
        const initialActiveTab = urlParams.get('active_tab');
        if (initialActiveTab) {
            const tabButton = document.querySelector(`.tab[data-tab="${initialActiveTab}"]`);
            if (tabButton) {
                // Имитируем клик, чтобы сработала общая логика переключения
                tabButton.click();
            }
        }

        // Логика выбора пользователей в таблице
        const selectAll = document.getElementById('selectAll');
        const userCheckboxes = document.querySelectorAll('.user-checkbox');
        const selectedCountSpan = document.getElementById('selectedCount');
        const deleteSelectedBtn = document.getElementById('deleteSelectedBtn');

        const updateSelectedCount = () => {
            if (!selectedCountSpan) return;
            const count = document.querySelectorAll('.user-checkbox:checked').length;
            selectedCountSpan.textContent = 'Выбрано: ' + count;
            if (deleteSelectedBtn) {
                deleteSelectedBtn.disabled = count === 0;
            }
        };

        if (selectAll) {
            selectAll.addEventListener('change', function () {
                userCheckboxes.forEach(cb => {
                    if (!cb.disabled) cb.checked = this.checked;
                });
                updateSelectedCount();
            });
        }
        
        if(userCheckboxes.length > 0) {
            userCheckboxes.forEach(cb => cb.addEventListener('change', updateSelectedCount));
            // Инициализация счетчика при загрузке
            updateSelectedCount();
        }

        // Логика кнопки массового удаления
        if (deleteSelectedBtn) {
            deleteSelectedBtn.addEventListener('click', function () {
                const selectedUserIds = Array.from(userCheckboxes)
                    .filter(cb => cb.checked && !cb.disabled)
                    .map(cb => cb.value);

                if (selectedUserIds.length === 0) {
                    alert('Пожалуйста, выберите хотя бы одного пользователя для удаления.');
                    return;
                }

                if (confirm('Вы уверены, что хотите удалить выбранных пользователей?')) {
                    const form = document.createElement('form');
                    form.method = 'POST';
                    // Берем action из data-атрибута
                    form.action = this.getAttribute('data-action'); 

                    selectedUserIds.forEach(userId => {
                        const input = document.createElement('input');
                        input.type = 'hidden';
                        input.name = 'user_ids';
                        input.value = userId;
                        form.appendChild(input);
                    });
                    
                    document.body.appendChild(form);
                    form.submit();
                }
            });
        }
    }
});

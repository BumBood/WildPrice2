// Обработчик добавления в избранное
document.addEventListener('DOMContentLoaded', function() {
  // Находим все кнопки добавления в избранное
  const favoriteButtons = document.querySelectorAll('.favorite-btn');
  
  // Добавляем обработчик для каждой кнопки
  favoriteButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault(); // Предотвращаем обновление страницы
      
      const isAuthenticated = button.getAttribute('data-authenticated') === 'True';
      const productId = button.getAttribute('data-product-id');
      
      if (isAuthenticated) {
        // Определяем, есть ли у кнопки класс 'active'
        const isActive = button.classList.contains('active');
        const url = isActive ? 
          `/delete_from_favourites/${productId}` : 
          `/add_to_favourites/${productId}`;
          
        // Отправляем AJAX запрос
        fetch(url, {
          method: 'GET',
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            if (isActive) {
              // Удаляем из избранного
              button.classList.remove('active');
              button.querySelector('i').classList.remove('fas');
              button.querySelector('i').classList.add('far');
              button.innerHTML = '<i class="far fa-heart mr-1"></i> В избранное';
            } else {
              // Добавляем в избранное
              button.classList.add('active');
              button.querySelector('i').classList.add('fas');
              button.querySelector('i').classList.remove('far');
              button.innerHTML = '<i class="fas fa-heart mr-1"></i> <span style="font-size: 0.9em;">Уже в избранном</span>';
            }
          }
        })
        .catch(error => console.error('Ошибка:', error));
      } else {
        // Перенаправляем на страницу регистрации
        window.location.href = '/register';
      }
    });
  });
  
  // Обработка кнопок удаления из избранного на странице избранного
  const removeFavoriteButtons = document.querySelectorAll('.remove-favorite-btn');
  removeFavoriteButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      
      const productId = button.getAttribute('data-product-id');
      
      fetch(`/delete_from_favourites/${productId}`, {
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Удаляем карточку товара из DOM
          const productCard = button.closest('.product-card');
          if (productCard) {
            productCard.remove();
          }
          
          // Проверяем, остались ли товары в избранном
          const remainingCards = document.querySelectorAll('.product-card');
          if (remainingCards.length === 0) {
            // Если товаров не осталось, показываем сообщение
            const container = document.querySelector('.row');
            if (container) {
              const emptyMessage = document.createElement('div');
              emptyMessage.className = 'empty-favourites';
              emptyMessage.innerHTML = `
                <div class="empty-icon">
                  <i class="fas fa-heart-broken" style="font-size: 2.5rem; color: var(--primary-color); opacity: 0.7;"></i>
                </div>
                <h3 class="mb-3">В избранном пока нет товаров</h3>
                <p class="text-muted mb-4">Добавляйте товары в избранное, чтобы не потерять их</p>
                <a href="/" class="btn">
                  <i class="fas fa-shopping-bag mr-2"></i>Перейти к товарам
                </a>
              `;
              container.parentNode.replaceChild(emptyMessage, container);
            }
          }
        }
      })
      .catch(error => console.error('Ошибка:', error));
    });
  });
}); 
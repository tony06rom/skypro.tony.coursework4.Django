document.addEventListener('DOMContentLoaded', function() {
  // Получаем текущий URL
  const currentUrl = window.location.pathname.split('/').pop() || 'main_page.html';

  // Находим все ссылки в меню
  const navLinks = document.querySelectorAll('.sidebar .nav-link');

  // Перебираем ссылки и сравниваем с текущим URL
  navLinks.forEach(link => {
    const linkUrl = link.getAttribute('href').split('/').pop();

    // Удаляем активный класс у всех ссылок
    link.classList.remove('active');

    // Если URL совпадает - добавляем активный класс
    if (currentUrl === linkUrl) {
      link.classList.add('active');
    }
  });
});
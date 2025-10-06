// Script para tela de login estilo Xmee
(function() {
  function init() {
    // Ocultar títulos originais
    var titles = document.querySelectorAll('h1, h2, h3, p');
    for (var i = 0; i < titles.length; i++) {
      var text = titles[i].textContent.trim();
      if (text.indexOf('Dashboard') !== -1 || 
          text.indexOf('Maremar') !== -1 ||
          text.indexOf('Sistema') !== -1) {
        titles[i].style.display = 'none';
      }
    }
    
    // Adicionar "Beyond Ocean" no card de login
    var button = document.querySelector('button');
    if (button && !document.getElementById('beyond-ocean-title')) {
      var beyondOcean = document.createElement('div');
      beyondOcean.id = 'beyond-ocean-title';
      beyondOcean.textContent = 'BEYOND OCEAN';
      
      // Inserir antes do botão
      button.parentNode.insertBefore(beyondOcean, button);
    }
    
    // Adicionar formas geométricas decorativas
    if (!document.querySelector('.geometric-shape-1')) {
      var shape1 = document.createElement('div');
      shape1.className = 'geometric-shape-1';
      document.body.appendChild(shape1);
      
      var shape2 = document.createElement('div');
      shape2.className = 'geometric-shape-2';
      document.body.appendChild(shape2);
      
      var circle = document.createElement('div');
      circle.className = 'geometric-circle';
      document.body.appendChild(circle);
    }
  }
  
  // Executar quando DOM estiver pronto
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  
  // Observar mudanças no DOM
  setTimeout(function() {
    var observer = new MutationObserver(init);
    observer.observe(document.body, { childList: true, subtree: true });
  }, 100);
})();

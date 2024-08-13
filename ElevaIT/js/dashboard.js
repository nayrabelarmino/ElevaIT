function showPostDetails(postId) {
    const mainTitle = document.getElementById('main-title');
    const insightsTitle = document.getElementById('insights-title');
    const postsTitle = document.getElementById('posts-title');
    const postDetails = document.getElementById('post-details');
    const pubsContainer = document.getElementById('pubs-container');
    const postImage = document.getElementById('post-image');
    const caption = document.getElementById('caption');
    const hashtags = document.getElementById('hashtags');
    const kpi1 = document.getElementById('kpi1');
    const kpi2 = document.getElementById('kpi2');
    const kpi3 = document.getElementById('kpi3');
    const kpi4 = document.getElementById('kpi4');

    // Muda os textos dos títulos
    mainTitle.textContent = 'Detalhes da Publicação';
    insightsTitle.textContent = 'Insights da Publicação';
    postsTitle.textContent = 'Publicação';

    // Esconde o container de publicações e mostra os detalhes da publicação
    postDetails.style.display = 'flex';
    pubsContainer.style.display = 'none';

    // Atualiza os KPIs e a imagem com base no postId
    switch (postId) {
        case 'post1':
            postImage.src = '../assets/post.jpg';
            caption.textContent = 'Esta é a legenda da primeira publicação no Instagram.';
            hashtags.textContent = '#marketing #socialmedia #engagement';
            kpi1.textContent = 126;
            kpi2.textContent = 52;
            kpi3.textContent = 38;
            kpi4.style.display = "none";
            break;
        case 'post2':
            postImage.src = '../assets/post2.jpg';
            caption.textContent = 'Legendas informativas para LinkedIn.';
            hashtags.textContent = '#linkedin #networking #business';
            kpi1.textContent = 230;
            kpi2.textContent = 70;
            kpi3.textContent = 40;
            kpi4.style.display = "none";
            break;
        case 'post3':
            postImage.src = '../assets/post3.jpg';
            caption.textContent = 'Você é mais forte do que imagina! Se junte a Inova Lopez para impulsionar sua empresa e alcançar os melhores resultados';
            hashtags.textContent = '#professional #career #linkedin';
            kpi1.textContent = 198;
            kpi2.textContent = 65;
            kpi3.textContent = 45;
            kpi4.style.display = "none";
            break;
        case 'post4':
            postImage.src = '../assets/post4.jpg';
            caption.textContent = 'Quarta publicação no Instagram com um bom engajamento.';
            hashtags.textContent = '#instagood #photooftheday #socialmedia';
            kpi1.textContent = 150;
            kpi2.textContent = 58;
            kpi3.textContent = 48;
            kpi4.style.display = "none";
            break;
        default:
            postImage.src = '';
            caption.textContent = '';
            hashtags.textContent = '';
            break;
    }
}

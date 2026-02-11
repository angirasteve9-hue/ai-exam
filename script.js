document.addEventListener('DOMContentLoaded', () => {
    const yesBtn = document.getElementById('yes-btn');
    const noBtn = document.getElementById('no-btn');
    const proposalCard = document.getElementById('proposal-card');
    const successMessage = document.getElementById('success-message');
    
    // Success State
    yesBtn.addEventListener('click', () => {
        proposalCard.style.display = 'none';
        successMessage.classList.remove('hidden');
        createConfetti();
    });

    // Runaway No Button
    const moveNoBtn = () => {
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const btnRect = noBtn.getBoundingClientRect();
        
        // Calculate random position but keep it within viewport
        // Subtract button dimensions to ensure it doesn't go off-screen
        const maxX = viewportWidth - btnRect.width - 20;
        const maxY = viewportHeight - btnRect.height - 20;
        
        const randomX = Math.max(20, Math.floor(Math.random() * maxX));
        const randomY = Math.max(20, Math.floor(Math.random() * maxY));
        
        // Use fixed positioning to move it anywhere on screen
        noBtn.style.position = 'fixed';
        noBtn.style.left = randomX + 'px';
        noBtn.style.top = randomY + 'px';
        
        // Add a funny tilt
        noBtn.style.transform = `rotate(${Math.floor(Math.random() * 40) - 20}deg)`;
    };

    noBtn.addEventListener('mouseover', moveNoBtn);
    noBtn.addEventListener('touchstart', (e) => {
        e.preventDefault(); // Prevent clicking on touch devices
        moveNoBtn();
    });
    noBtn.addEventListener('click', moveNoBtn); // Just in case

    // Floating Hearts Background
    function createHeart() {
        const heart = document.createElement('div');
        heart.classList.add('heart');
        heart.innerHTML = '💖'; // You can vary this: 💖, 💕, 💗, 💓
        
        // Randomize origin and size
        heart.style.left = Math.random() * 100 + 'vw';
        heart.style.animationDuration = Math.random() * 5 + 10 + 's'; // 10-15s
        heart.style.fontSize = Math.random() * 20 + 10 + 'px'; // 10-30px
        
        document.body.appendChild(heart);
        
        // Clean up
        setTimeout(() => {
            heart.remove();
        }, 15000); // Match max animation duration
    }

    // Start creating hearts
    setInterval(createHeart, 500);

    // Simple Confetti for Success
    function createConfetti() {
        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.style.position = 'fixed';
            confetti.style.left = Math.random() * 100 + 'vw';
            confetti.style.top = -10 + 'px';
            confetti.style.width = '10px';
            confetti.style.height = '10px';
            confetti.style.backgroundColor = ['#FFD1DC', '#FF7E9C', '#FFF', '#FFB7B2'][Math.floor(Math.random() * 4)];
            confetti.style.animation = `floatUp ${Math.random() * 3 + 2}s linear reverse`; // Fall down
            
            // Custom fall animation for confetti would be better, reusing floatUp in reverse for simplicity
            // or just simple JS animation/transition
            
            // Let's rely on CSS for better performance, but we need a fall keyframe.
            // Adding it dynamically:
            confetti.style.transition = `top ${Math.random() * 2 + 3}s ease-in, transform ${Math.random() * 2 + 3}s linear`;
            
            document.body.appendChild(confetti);
            
            // Trigger animation
            setTimeout(() => {
                confetti.style.top = '110vh';
                confetti.style.transform = `rotate(${Math.random() * 360}deg)`;
            }, 100);

            setTimeout(() => confetti.remove(), 5000);
        }
    }
});

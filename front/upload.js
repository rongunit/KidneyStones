const uploadButton = document.getElementById('upload-button')
const homeButton = document.getElementById('home-button')

homeButton.addEventListener('click', async() =>{
    window.location.href = 'home.html';
})

const form = document.getElementById('file-upload-form');

form.onsubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    try {
        const response = await fetch('http://localhost:8000/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById('response').innerText = data.message + "\n " + data['File names'];
        } else {
            console.error('Failed to upload files');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

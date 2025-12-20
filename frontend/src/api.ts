import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000', // Assuming default FastAPI port
    headers: {
        'Content-Type': 'application/json',
    },
});

export default api;

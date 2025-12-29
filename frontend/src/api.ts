import axios, { AxiosError } from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 second timeout
});

// Request interceptor for logging
api.interceptors.request.use(
    (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
    },
    (error) => {
        console.error('Request error:', error);
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => {
        // Successful responses pass through
        return response;
    },
    (error: AxiosError) => {
        // Handle different types of errors
        if (error.response) {
            // Server responded with error status
            const status = error.response.status;
            const data = error.response.data as any;

            console.error(`API Error ${status}:`, data);

            // Provide user-friendly error messages
            switch (status) {
                case 400:
                    error.message = data?.detail || 'İstek geçersiz. Lütfen girdiğiniz bilgileri kontrol edin.';
                    break;
                case 401:
                    error.message = 'Oturum süreniz dolmuş. Lütfen tekrar giriş yapın.';
                    break;
                case 403:
                    error.message = 'Bu işlem için yetkiniz yok.';
                    break;
                case 404:
                    error.message = data?.detail || 'İstenilen kaynak bulunamadı.';
                    break;
                case 409:
                    error.message = data?.detail || 'Bu işlem bir çakışmaya neden oldu.';
                    break;
                case 422:
                    error.message = data?.detail || 'Gönderilen veri doğrulanamadı.';
                    break;
                case 500:
                    error.message = data?.detail || 'Sunucu hatası oluştu. Lütfen daha sonra tekrar deneyin.';
                    break;
                case 502:
                case 503:
                case 504:
                    error.message = 'Sunucu şu anda kullanılamıyor. Lütfen daha sonra tekrar deneyin.';
                    break;
                default:
                    error.message = data?.detail || `Bir hata oluştu (${status}).`;
            }
        } else if (error.request) {
            // Request made but no response received
            console.error('No response received:', error.request);
            if (error.code === 'ECONNABORTED') {
                error.message = 'İstek zaman aşımına uğradı. Lütfen tekrar deneyin.';
            } else if (error.code === 'ERR_NETWORK') {
                error.message = 'Ağ bağlantısı hatası. İnternet bağlantınızı kontrol edin.';
            } else {
                error.message = 'Sunucuya bağlanılamadı. Lütfen internet bağlantınızı kontrol edin.';
            }
        } else {
            // Something else happened
            console.error('Request setup error:', error.message);
            error.message = error.message || 'Beklenmeyen bir hata oluştu.';
        }

        return Promise.reject(error);
    }
);

export default api;

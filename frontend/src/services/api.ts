/**API Service*/

import axios, { AxiosInstance } from 'axios';
import { ApiResponse, User, AuthTokens, Strategy, Signal, Trade, Position, PerformanceMetrics } from '../types/api';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.token = localStorage.getItem('access_token');
    this.setupInterceptors();
  }

  private setupInterceptors() {
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  // Auth endpoints
  async register(username: string, email: string, password: string, full_name?: string): Promise<AuthTokens> {
    const response = await this.client.post<ApiResponse<AuthTokens>>('/auth/register', {
      username,
      email,
      password,
      full_name,
    });
    return response.data.data!;
  }

  async login(username: string, password: string): Promise<AuthTokens> {
    const response = await this.client.post<ApiResponse<AuthTokens>>('/auth/login', {
      username,
      password,
    });
    return response.data.data!;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<ApiResponse<User>>('/auth/me');
    return response.data.data!;
  }

  async logout(): Promise<void> {
    await this.client.post('/auth/logout');
    localStorage.removeItem('access_token');
    this.token = null;
  }

  async changePassword(data: { old_password: string; new_password: string }): Promise<any> {
    const response = await this.client.post<ApiResponse<any>>('/auth/change-password', data);
    return response.data.data;
  }

  // Strategies endpoints
  async getStrategies(): Promise<Strategy[]> {
    const response = await this.client.get<ApiResponse<Strategy[]>>('/strategies');
    return response.data.data || [];
  }

  async getStrategyDetails(name: string): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>(`/strategies/${name}`);
    return response.data.data;
  }

  async getStrategyPerformance(name: string): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>(`/strategies/${name}/performance`);
    return response.data.data;
  }

  async startStrategy(name: string): Promise<any> {
    const response = await this.client.post<ApiResponse<any>>(`/strategies/${name}/start`);
    return response.data.data;
  }

  async stopStrategy(name: string): Promise<any> {
    const response = await this.client.post<ApiResponse<any>>(`/strategies/${name}/stop`);
    return response.data.data;
  }

  // Signals endpoints
  async getSignals(skip: number = 0, limit: number = 20): Promise<Signal[]> {
    const response = await this.client.get<ApiResponse<Signal[]>>(`/signals?skip=${skip}&limit=${limit}`);
    return response.data.data || [];
  }

  async executeSignal(signalId: string): Promise<any> {
    const response = await this.client.post<ApiResponse<any>>(`/signals/${signalId}/execute`);
    return response.data.data;
  }

  async cancelSignal(signalId: string): Promise<any> {
    const response = await this.client.post<ApiResponse<any>>(`/signals/${signalId}/cancel`);
    return response.data.data;
  }

  // Trades endpoints
  async getTrades(skip: number = 0, limit: number = 20): Promise<Trade[]> {
    const response = await this.client.get<ApiResponse<Trade[]>>(`/trades?skip=${skip}&limit=${limit}`);
    return response.data.data || [];
  }

  async getTrade(tradeId: string): Promise<Trade> {
    const response = await this.client.get<ApiResponse<Trade>>(`/trades/${tradeId}`);
    return response.data.data!;
  }

  async getTradeSummary(): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>('/trades/summary');
    return response.data.data;
  }

  async getTradeStatistics(): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>('/trades/statistics');
    return response.data.data;
  }

  // Positions endpoints
  async getPositions(): Promise<Position[]> {
    const response = await this.client.get<ApiResponse<Position[]>>('/positions');
    return response.data.data || [];
  }

  async getPositionsSummary(): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>('/positions/summary');
    return response.data.data;
  }

  async closePosition(positionId: string): Promise<any> {
    const response = await this.client.post<ApiResponse<any>>(`/positions/${positionId}/close`);
    return response.data.data;
  }

  // Prices endpoints
  async getPrice(symbol: string): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>(`/prices/${symbol}`);
    return response.data.data;
  }

  async getPriceChart(symbol: string, period: string = '1D', interval: string = '1H'): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>(
      `/prices/${symbol}/chart?period=${period}&interval=${interval}`
    );
    return response.data.data;
  }

  // Account endpoints
  async getBalance(): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>('/account/balance');
    return response.data.data;
  }

  async getAccountInfo(): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>('/account/info');
    return response.data.data;
  }

  // Credentials endpoints
  async addCredentials(data: { broker: string; api_key: string; api_secret: string }): Promise<any> {
    const response = await this.client.post<ApiResponse<any>>('/credentials', data);
    return response.data.data;
  }

  async getCredentials(): Promise<any[]> {
    const response = await this.client.get<ApiResponse<any[]>>('/credentials');
    return response.data.data || [];
  }

  async deleteCredentials(credentialId: string): Promise<any> {
    const response = await this.client.delete<ApiResponse<any>>(`/credentials/${credentialId}`);
    return response.data.data;
  }

  async testCredentials(credentialId: string): Promise<any> {
    const response = await this.client.post<ApiResponse<any>>(`/credentials/${credentialId}/test`);
    return response.data.data;
  }

  // Analytics endpoints
  async getPerformance(): Promise<PerformanceMetrics> {
    const response = await this.client.get<ApiResponse<PerformanceMetrics>>('/analytics/performance');
    return response.data.data!;
  }

  async getStrategiesPerformance(): Promise<any[]> {
    const response = await this.client.get<ApiResponse<any[]>>('/analytics/strategies');
    return response.data.data || [];
  }

  async getMonthlyReturns(year: number = 2026): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>(`/analytics/monthly-returns?year=${year}`);
    return response.data.data;
  }

  async getEquityCurve(period: string = '1M'): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>(`/analytics/equity-curve?period=${period}`);
    return response.data.data;
  }
}

export const apiClient = new ApiClient();

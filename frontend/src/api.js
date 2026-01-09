// API 基础配置和工具函数
const API_BASE_URL = "http://localhost:11451/api/v1";

/**
 * 获取认证 token
 */
function getAuthToken() {
    return localStorage.getItem("auth_token");
}

/**
 * 发送 HTTP 请求的通用函数
 */
async function request(endpoint, options = {}) {
    const { method = "GET", body, headers = {}, requiresAuth = true } = options;

    const config = {
        method,
        headers: {
            "Content-Type": "application/json",
            ...headers,
        },
    };

    // 添加认证 token
    if (requiresAuth) {
        const token = getAuthToken();
        if (token) {
            config.headers["Authorization"] = `Bearer ${token}`;
        }
    }

    // 添加请求体
    if (body) {
        config.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "Request failed");
        }

        return data;
    } catch (error) {
        console.error("API request error:", error);
        throw error;
    }
}

// 认证相关 API
export const authAPI = {
    /**
     * 用户登录
     */
    async login(account, password, role) {
        const response = await request("/auth/login", {
            method: "POST",
            body: { account, password, role },
            requiresAuth: false,
        });

        // 保存 token
        if (response.data?.access_token) {
            localStorage.setItem("auth_token", response.data.access_token);
            localStorage.setItem("user_info", JSON.stringify(response.data.user));
        }

        return response;
    },

    /**
     * 用户注册
     */
    async register(userData) {
        return await request("/auth/register", {
            method: "POST",
            body: userData,
            requiresAuth: false,
        });
    },

    /**
     * 获取当前用户信息
     */
    async getCurrentUser() {
        const response = await request("/auth/me");
        if (response.data) {
            localStorage.setItem("user_info", JSON.stringify(response.data));
        }
        return response;
    },

    /**
     * 登出
     */
    logout() {
        localStorage.removeItem("auth_token");
        localStorage.removeItem("user_info");
    },
};

// 用户资料相关 API
export const userAPI = {
    /**
     * 获取个人资料
     */
    async getProfile() {
        return await request("/users/me/profile");
    },

    /**
     * 更新个人资料
     */
    async updateProfile(profileData) {
        return await request("/users/me/profile", {
            method: "PUT",
            body: profileData,
        });
    },
};

// 设备相关 API
export const deviceAPI = {
    /**
     * 获取设备列表
     */
    async list(params = {}) {
        const query = new URLSearchParams(params).toString();
        return await request(`/devices?${query}`);
    },

    /**
     * 获取设备详情
     */
    async get(id) {
        return await request(`/devices/${id}`);
    },

    /**
     * 获取设备可用性
     */
    async availability(params = {}) {
        const query = new URLSearchParams(params).toString();
        return await request(`/devices/availability?${query}`);
    },

    /**
     * 获取设备台账统计
     */
    async ledgerStats() {
        return await request("/devices/ledger/stats");
    },
};

// 预约相关 API
export const reservationAPI = {
    /**
     * 获取预约列表
     */
    async list(status, skip = 0, limit = 100) {
        let endpoint = `/reservations?skip=${skip}&limit=${limit}`;
        if (status) {
            endpoint += `&status=${status}`;
        }
        return await request(endpoint);
    },

    /**
     * 获取预约详情
     */
    async get(id) {
        return await request(`/reservations/${id}`);
    },

    /**
     * 创建预约
     */
    async create(data) {
        return await request("/reservations", {
            method: "POST",
            body: data,
        });
    },

    /**
     * 更新预约
     */
    async update(id, data) {
        return await request(`/reservations/${id}`, {
            method: "PUT",
            body: data,
        });
    },

    /**
     * 删除预约
     */
    async delete(id) {
        return await request(`/reservations/${id}`, {
            method: "DELETE",
        });
    }
};

// 人员台账相关 API
export const staffAPI = {
    /**
     * 获取人员台账统计
     */
    async stats() {
        return await request("/staff/stats");
    },

    /**
     * 获取学生台账列表
     */
    async listStudents(params = {}) {
        const query = new URLSearchParams(params).toString();
        const endpoint = query ? `/staff/students?${query}` : "/staff/students";
        return await request(endpoint);
    },

    /**
     * 创建学生台账
     */
    async createStudent(data) {
        return await request("/staff/students", {
            method: "POST",
            body: data,
        });
    },

    /**
     * 更新学生台账
     */
    async updateStudent(id, data) {
        return await request(`/staff/students/${id}`, {
            method: "PUT",
            body: data,
        });
    },

    /**
     * 删除学生台账
     */
    async deleteStudent(id) {
        return await request(`/staff/students/${id}`, {
            method: "DELETE",
        });
    },
};

/**
 * 从 localStorage 获取用户信息
 */
export function getCachedUserInfo() {
    const userInfo = localStorage.getItem("user_info");
    return userInfo ? JSON.parse(userInfo) : null;
}

/**
 * 检查是否已登录
 */
export function isAuthenticated() {
    return !!getAuthToken();
}

<template>
  <div class="login-page" data-testid="login-page">
    <div class="login-page__card">
      <h1 class="login-page__title">Вход</h1>

      <form class="login-page__form" @submit.prevent="submit">
        <BaseInput
          v-model="username"
          label="Логин"
          placeholder="admin"
          data-testid="login-username"
        />
        <BaseInput
          v-model="password"
          label="Пароль"
          type="password"
          placeholder="••••••••"
          data-testid="login-password"
        />

        <p v-if="error" class="login-page__error" data-testid="login-error">
          {{ error }}
        </p>

        <button
          type="submit"
          class="btn btn_primary login-page__submit"
          :disabled="loading"
          data-testid="login-submit"
        >
          {{ loading ? "Вход..." : "Войти" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/authStore";
import BaseInput from "@/components/BaseInput/BaseInput.vue";

const router = useRouter();
const authStore = useAuthStore();
const username = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

async function submit() {
  error.value = "";
  loading.value = true;
  try {
    await authStore.login({
      username: username.value,
      password: password.value,
    });
    router.push("/");
  } catch (e: unknown) {
    error.value =
      (e as { response?: { data?: { detail?: string } } })?.response?.data
        ?.detail || "Ошибка входа";
  } finally {
    loading.value = false;
  }
}
</script>

<style lang="scss" scoped>
@use "@/styles/variables" as *;

.login-page__error {
  margin: 0;
  font-size: 0.875rem;
  color: $danger;
}

.btn {
  padding: 0.6rem 1.25rem;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  &_primary {
    background: $primary;
    color: #fff;
    &:hover:not(:disabled) {
      background: $primary-hover;
    }
    &:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }
  }
}
</style>

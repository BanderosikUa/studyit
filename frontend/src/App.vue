<script setup>
import { computed } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const isAuthenticated = computed(() => authStore.isAuthenticated)
const navigationItems = [
  {
    label: 'Дашборд',
    to: { name: 'Dashboard' },
    names: ['Dashboard'],
  },
  {
    label: 'Теми',
    to: { name: 'Topics' },
    names: ['Topics', 'TopicDetail'],
  },
  {
    label: 'Тренажер',
    to: { name: 'TrainerSetup' },
    names: ['TrainerSetup', 'TrainerSession', 'TrainerResults'],
  },
]

function logout() {
  authStore.logout()
  router.push('/login')
}

function isActiveLink(names) {
  return names.includes(route.name)
}
</script>

<template>
  <div class="app-shell">
    <div class="app-shell__aurora"></div>
    <div class="app-shell__veil"></div>
    <div class="app-shell__content">
      <nav v-if="isAuthenticated" class="app-nav">
        <div class="app-nav__inner">
          <router-link :to="{ name: 'Dashboard' }" class="brand-mark">
            <span class="brand-mark__halo"></span>
            <span class="brand-mark__title">StudyIt</span>
          </router-link>
          <div class="app-nav__links">
            <router-link
              v-for="item in navigationItems"
              :key="item.label"
              :to="item.to"
              class="app-nav__link"
              :class="{ 'app-nav__link--active': isActiveLink(item.names) }"
            >
              {{ item.label }}
            </router-link>
            <button type="button" class="app-nav__ghost" @click="logout">Вийти</button>
          </div>
        </div>
      </nav>
      <main class="app-main" :class="{ 'app-main--guest': !isAuthenticated }">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

.app-shell__aurora,
.app-shell__veil {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.app-shell__aurora {
  background:
    radial-gradient(circle at 15% 0%, rgba(79, 168, 255, 0.24), transparent 34%),
    radial-gradient(circle at 82% 12%, rgba(255, 159, 90, 0.18), transparent 26%),
    radial-gradient(circle at 50% 100%, rgba(17, 37, 81, 0.08), transparent 32%);
  filter: blur(18px);
}

.app-shell__veil {
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.36), transparent 34%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.24), transparent 26%);
}

.app-shell__content {
  position: relative;
  z-index: 1;
  min-height: 100vh;
}

.app-nav {
  position: sticky;
  top: 0;
  z-index: 20;
  padding: 1rem 1rem 0;
}

.app-nav__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  width: min(1180px, 100%);
  margin: 0 auto;
  padding: 0.95rem 1.1rem;
  border: 1px solid rgba(172, 194, 233, 0.22);
  border-radius: 1.4rem;
  background: linear-gradient(135deg, rgba(10, 24, 55, 0.86), rgba(17, 37, 81, 0.74));
  box-shadow: 0 18px 40px rgba(17, 37, 81, 0.2);
  backdrop-filter: blur(18px);
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  gap: 0.8rem;
  min-width: 0;
}

.brand-mark__halo {
  width: 0.85rem;
  height: 0.85rem;
  border-radius: 999px;
  background:
    radial-gradient(circle at 30% 30%, #f6fbff 0%, #9dd5ff 40%, #4fa8ff 68%, #2357d8 100%);
  box-shadow:
    0 0 0 0.4rem rgba(79, 168, 255, 0.14),
    0 0 24px rgba(79, 168, 255, 0.55);
}

.brand-mark__title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #f7fbff;
}

.app-nav__links {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.7rem;
}

.app-nav__link,
.app-nav__ghost {
  padding: 0.7rem 1rem;
  border: 0;
  border-radius: 999px;
  font-size: 0.95rem;
  font-weight: 700;
  color: rgba(236, 244, 255, 0.78);
  background: transparent;
  transition:
    color 180ms ease,
    background-color 180ms ease,
    transform 180ms ease,
    box-shadow 180ms ease;
}

.app-nav__link:hover,
.app-nav__ghost:hover {
  color: #f9fcff;
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-1px);
}

.app-nav__link--active {
  color: #f9fcff;
  background:
    linear-gradient(135deg, rgba(79, 168, 255, 0.24), rgba(255, 255, 255, 0.08));
  box-shadow: inset 0 0 0 1px rgba(167, 214, 255, 0.18);
}

.app-main {
  width: min(1180px, 100%);
  margin: 0 auto;
  padding: 1.5rem 1rem 3rem;
}

.app-main--guest {
  display: grid;
  align-items: center;
  min-height: calc(100vh - 4rem);
  padding-top: 3rem;
}

@media (max-width: 768px) {
  .app-nav {
    padding-top: 0.8rem;
  }

  .app-nav__inner {
    align-items: flex-start;
    flex-direction: column;
    border-radius: 1.2rem;
    padding: 0.9rem;
  }

  .app-nav__links {
    width: 100%;
    justify-content: flex-start;
  }

  .app-nav__link,
  .app-nav__ghost {
    padding-inline: 0.9rem;
  }

  .app-main {
    padding-top: 1.1rem;
  }
}
</style>

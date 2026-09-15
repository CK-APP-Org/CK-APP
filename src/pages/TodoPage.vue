<template>
  <div class="view-toggle-container">
    <q-btn-toggle
      v-model="currentView"
      toggle-color="primary"
      spread
      :options="[
        { label: '月曆', value: 'calendar' },
        { label: '待辦', value: 'todoList' },
      ]"
      class="q-mb-md"
      style="width: 270px"
    />
  </div>

  <calendar-view
    ref="calendarViewRef"
    :events="events"
    :todos="todos"
    :school-events="schoolEvents"
    :current-view="currentView"
    @edit-event="handleEditEvent"
  />
  <todo-list-view
    :todos="todos"
    :todo-categories="todoCategories"
    :current-view="currentView"
    @todo-checked="handleTodoChecked"
    @manage-categories="handleManageTodoCategories"
  />

  <div class="add-button-container">
    <button class="add-button" @click="toggleMenu">+</button>
    <div v-if="showMenu" class="add-menu">
      <button class="menu-item" @click="openTodoDialog">💼待辦</button>
      <button class="menu-item" @click="openEventDialog">📅活動</button>
    </div>
  </div>

  <event-dialog
    ref="eventDialogRef"
    v-model="showEventDialog"
    :is-editing="isEditing"
    :event-categories="eventCategories"
    :initial-event="editingEvent"
    @save="handleEventSaved"
    @delete="handleEventDeleted"
  />

  <todo-dialog
    ref="todoDialogRef"
    v-model="showTodoDialog"
    :todo-categories="todoCategories"
  />
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useStore } from "vuex";
import CalendarView from "../components/todo/CalendarView.vue";
import TodoListView from "../components/todo/TodoListView.vue";
import EventDialog from "../components/todo/EventDialog.vue";
import TodoDialog from "../components/todo/TodoDialog.vue";
import { SCHOOL_EVENTS, loadSchoolEvents } from "../data/calendar";

const store = useStore();

// Term 行事曆, read-only. Renders from the bundled copy straight away, then
// takes the Data repo's copy if it is reachable -- the school revises the
// calendar mid-year. See src/data/calendar.
const schoolEvents = ref(SCHOOL_EVENTS);

onMounted(async () => {
  schoolEvents.value = await loadSchoolEvents();
});

const events = computed(() => store.getters.getEvents);
const eventCategories = computed(() => store.getters.getEventCategories);
const todos = computed(() => store.getters.getTodos);
const todoCategories = computed(() => store.getters.getTodoCategories);
const currentView = computed({
  get: () => store.getters.getCurrentView,
  set: (value) => store.dispatch("updateCurrentView", value),
});

const showMenu = ref(false);
const showEventDialog = ref(false);
const isEditing = ref(false);
const editingEvent = ref(null);
const showTodoDialog = ref(false);

const calendarViewRef = ref(null);
const eventDialogRef = ref(null);
const todoDialogRef = ref(null);

const toggleMenu = () => {
  showMenu.value = !showMenu.value;
};

const openTodoDialog = () => {
  showTodoDialog.value = true;
  showMenu.value = false;
};

const openEventDialog = () => {
  isEditing.value = false;
  editingEvent.value = null;
  showEventDialog.value = true;
  showMenu.value = false;
};

const handleEditEvent = (event) => {
  editingEvent.value = event;
  isEditing.value = true;
  showEventDialog.value = true;
};

const handleEventSaved = () => {
  calendarViewRef.value?.updateSelectedDayEvents();
};

const handleEventDeleted = () => {
  calendarViewRef.value?.updateSelectedDayEvents();
};

const handleTodoChecked = (todoId) => {
  // Delay matches the original: gives the .todo-item-completed CSS
  // transition time to play before the item leaves the store/list.
  setTimeout(() => {
    store.dispatch("deleteTodo", todoId);
  }, 500);
};

const handleManageTodoCategories = () => {
  todoDialogRef.value?.openCategoryManager();
};
</script>

<style scoped>
.view-toggle-container {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.add-button-container {
  position: fixed;
  bottom: 140px;
  right: 20px;
  z-index: 2000;
}

.add-button {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #c10015;
  color: white;
  font-size: 24px;
  border: none;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
}

.add-menu {
  position: absolute;
  bottom: 60px;
  right: 0;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 95px;
  z-index: 10;
}

.add-menu .menu-item {
  display: block;
  width: 100%;
  padding: 12px 10px;
  font-size: 17px;
  border: none;
  background-color: transparent;
  cursor: pointer;
  text-align: center;
  white-space: nowrap;
}

.add-menu button {
  display: block;
  width: 100%;
  padding: 10px 20px;
  border: none;
  background-color: transparent;
  cursor: pointer;
  text-align: left;
}
</style>

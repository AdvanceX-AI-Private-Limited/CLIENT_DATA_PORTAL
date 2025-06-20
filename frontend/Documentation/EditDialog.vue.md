PATH `/frontend/src/components/OutletManagement/EditDialog.vue` component to help you or your team reuse it easily in the future.

---

## 🧾 `EditDialog.vue` — Documentation

`EditDialog` is a reusable modal form component for editing structured data objects. It takes an object, filters editable fields based on passed rules, and emits the edited result upon validation.

---

### 🔧 Props

| Prop          | Type                  | Description                                          |
| ------------- | --------------------- | ---------------------------------------------------- |
| `visible`     | `Boolean`             | Controls modal visibility                            |
| `row`         | `Object`              | The data row to be edited                            |
| `editAllowed` | `Object`              | A map of keys indicating which fields are editable   |
| `mapHeaders`  | `Object`              | A mapping of field keys to human-readable labels     |
| `apiError`    | `String/Boolean/null` | Optional error message to display from API           |
| `apiSuccess`  | `Boolean`             | Optional success indicator (can be styled if needed) |
| `loading`     | `Boolean`             | Disables form interaction while loading              |

---

### 📤 Emits

| Event    | Payload             | Description                                      |
| -------- | ------------------- | ------------------------------------------------ |
| `close`  | –                   | Emitted when dialog is closed                    |
| `save`   | `Object` (optional) | Can be used as an alternate submit event         |
| `submit` | `Object`            | Emitted when form is valid and submit is clicked |

---

### ✏️ Internal Logic

* **Form State:** Uses a reactive `form` object, initialized with the `row` prop.
* **Editable Fields:** Computed from `mapHeaders` and filtered by `editAllowed`.
* **Validation:** Basic non-empty field check for editable fields.
* **Change Detection:** Only allows submission if at least one editable field is modified.
* **Aggregator Field Special Case:** Rendered as a `<select>` instead of a text input.

---

### 📥 Usage Example

#### Import & Register:

```vue
<script setup>
import EditDialog from '@/components/OutletManagement/EditDialog.vue';
</script>
```

#### Use in Template:

```vue
<EditDialog
  :visible="editDialogVisible"
  :row="editRow"
  :edit-allowed="editAllowed"
  :map-headers="mapHeaders"
  :api-error="updateApiError"
  :loading="loading"
  :api-success="updateApiSuccess"
  @close="editDialogVisible = false"
  @submit="handleUpdateApi"
/>
```

#### Sample `editAllowed`:

```js
const editAllowed = {
  aggregator: true,
  resid: true,
  subzone: true,
  city: true,
  outletnumber: true,
};
```

#### Sample `mapHeaders`:

```js
const mapHeaders = {
  aggregator: "Aggregator",
  resid: "Res ID",
  subzone: "Subzone",
  city: "City",
  outletnumber: "Outlet Number",
};
```

#### Sample `handleUpdateApi`:

```js
async function handleUpdateApi(payload) {
  const params = {
    outlet_id: editRow.value.id,
    payload: {
      ...payload,
      client_id: editRow.value.client_id
    }
  };
  await updateOutlet(params); // API call
}
```

---

### ✅ Best Practices

* Always validate inputs via `validateForm()` before submission.
* Ensure the `row` has values for all keys in `editAllowed` or handle missing keys gracefully.
* Use the `apiError` prop to display errors returned from your backend API.
* Use `loading` prop to show a spinner and disable the UI while processing.

---

### 🎨 Styling & Transitions

* Uses TailwindCSS for form and modal styling.
* `@click.self="$emit('close')"` allows modal background click to dismiss.
* Smooth fade-in animation is applied on modal.


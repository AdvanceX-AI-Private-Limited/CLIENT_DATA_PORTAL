import { ref } from 'vue';

const email = ref('');
const client_id = ref('');

export function currentUserData() {
    return {
        email,
        client_id
    }
}
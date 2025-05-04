const api = 'http://http://38.180.205.35/:8000';


const pS = document.getElementById('product-select');
const uS = document.getElementById('user-select');
const qty = document.getElementById('quantity');
const cS = document.getElementById('unitCost');
const d = document.getElementById('declarationDate');
const resultPre = document.getElementById('result');
const pf = document.getElementById('product-form');
const pn = document.getElementById('product-name');
const ph = document.getElementById('product-hs-code');
const pci = document.getElementById('product-category-id');
const pco = document.getElementById('product-country-id');
const pres = document.getElementById('product-result');
const payload = {
    name: pn.value.trim(),
    hs_code: ph.value.trim(),
    category_id: Number(document.getElementById('product-category-id').value),
    country_id: Number(document.getElementById('product-country-id').value)
};


async function loadOptions() {
    try {
        const [prods, users, cats, cts] = await Promise.all([
            fetch(`${api}/products`).then(r => r.json()),
            fetch(`${api}/users`).then(r => r.json()),
            fetch(`${api}/categories`).then(r => r.json()),
            fetch(`${api}/countries`).then(r => r.json())
        ]);

        prods.forEach(p => pS.append(new Option(p.name, p.id)));
        users.forEach(u => uS.append(new Option(u.email, u.id)));

        const catSelect = document.getElementById('product-category-id');
        cats.forEach(c => catSelect.append(new Option(c.name, c.id)));

        const countrySelect = document.getElementById('product-country-id');
        cts.forEach(c => countrySelect.append(new Option(c.name, c.id)));
    } catch (err) {
        console.error('Failed to load options', err);
    }
}

async function loadDeclarations() {
    try {
        const decls = await fetch(`${api}/declarations`).then(r => r.json());
        const tb = document.querySelector('#declarations-table tbody');
        tb.innerHTML = '';
        decls.forEach(d => {
            const tr = tb.insertRow();
            tr.innerHTML = `
          <td>${d.id}</td>
          <td>${d.product_id}</td>
          <td>${d.user_id}</td>
          <td>${d.quantity}</td>
          <td>${d.unit_cost}</td>
          <td>${d.due}</td>
          <td>${d.declaration_date}</td>
          <td>${d.status}</td>
          <td>${
                d.status === 'submitted'
                    ? `<button onclick="pay(${d.id})">Pay</button>`
                    : ''
            }</td>
        `;
        });
    } catch (err) {
        console.error('Failed to load declarations', err);
    }
}

document.getElementById('declaration-form').onsubmit = async e => {
    e.preventDefault();
    try {
        const payload = {
            product_id: +pS.value,
            user_id: +uS.value,
            quantity: +qty.value,
            unit_cost: +cS.value,
            declaration_date: d.value
        };
        const res = await fetch(`${api}/declarations`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        document.getElementById('declaration-result').textContent = 'Declaration successfully created!';
        await loadDeclarations();
    } catch (err) {
        console.error('Create failed', err);
    }
};

window.pay = async id => {
    try {
        await fetch(`${api}/declarations/${id}/pay`, {method: 'POST'});
        await loadDeclarations();
    } catch (err) {
        console.error('Pay failed', err);
    }
};

document.getElementById('user-form').onsubmit = async e => {
    e.preventDefault();
    try {
        const payload = {
            email: document.getElementById('user-email').value,
            company: document.getElementById('user-company').value
        };
        const res = await fetch(`${api}/users`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        document.getElementById('user-result').textContent = 'User successfully created!';
    } catch (err) {
        console.error('User creation failed', err);
    }
};


pf.onsubmit = async e => {
    e.preventDefault();

    const payload = {
        name: pn.value.trim(),
        hs_code: ph.value.trim(),
        category_id: Number(pci.value),
        country_id: Number(pco.value)
    };
    if (!payload.name || !payload.hs_code ||
        !Number.isInteger(payload.category_id) ||
        !Number.isInteger(payload.country_id)) {
        alert("All fields are required and IDs must be integers");
        return;
    }

    try {
        const res = await fetch(`${api}/products`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const text = await res.text();
        if (!res.ok) {
            console.error("Product creation failed:", res.status, text);
            return;
        }
        document.getElementById('product-result').textContent = 'Product successfully created!';
    } catch (err) {
        console.error("Fetch error:", err);
    }
};

// initialize
loadOptions().then(loadDeclarations);

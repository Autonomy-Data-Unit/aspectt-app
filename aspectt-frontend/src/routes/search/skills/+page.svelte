<script lang="ts">
	import { searchBySkill } from '$lib/api/client';

	let query = $state('');
	let results = $state<Array<{ uk_soc_2020: number; title: string; skill_name: string; importance: number; level: number }>>([]);
	let total = $state(0);
	let loading = $state(false);
	let searched = $state(false);
	let currentPage = $state(0);
	const perPage = 50;

	let debounceTimer: ReturnType<typeof setTimeout>;

	async function doSearch() {
		if (!query.trim()) { results = []; total = 0; searched = false; return; }
		loading = true;
		searched = true;
		currentPage = 0;
		await load();
	}

	async function load() {
		loading = true;
		const data = await searchBySkill(query, perPage, currentPage * perPage);
		results = data.results;
		total = data.total;
		loading = false;
	}

	function onInput() {
		clearTimeout(debounceTimer);
		if (!query.trim()) { results = []; total = 0; searched = false; return; }
		debounceTimer = setTimeout(() => doSearch(), 300);
	}

	function onKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') { clearTimeout(debounceTimer); doSearch(); }
	}
</script>

<svelte:head><title>Skills search - ASPECTT</title></svelte:head>

<div class="container">
	<h1 class="page-title">Skills search</h1>
	<p class="page-desc">Find occupations that require a given skill, ranked by importance.</p>

	<div class="card">
		<div class="search-row">
			<input class="search-input" type="text" placeholder="e.g. Programming, Critical Thinking, Negotiation..."
				bind:value={query} oninput={onInput} onkeydown={onKeydown} />
			<button class="btn btn-primary" onclick={doSearch}>Search</button>
		</div>
	</div>

	{#if loading}
		<div class="loading"><div class="spinner"></div></div>
	{:else if searched}
		<div class="card">
			<h2>Occupations requiring "{query}" ({total})</h2>
			{#if results.length === 0}
				<p class="no-results">No occupations found with skill matching "{query}"</p>
			{:else}
				<div class="results">
					{#each results as r}
						<a href="/occupation/{r.uk_soc_2020}" class="result-row">
							<span class="occ-code">{r.uk_soc_2020}</span>
							<span class="occ-title">{r.title}</span>
							<span class="skill-name">{r.skill_name}</span>
							<div class="bar-wrap">
								<div class="bar-fill" style="width: {(r.importance / 5) * 100}%"></div>
							</div>
							<span class="val">{r.importance?.toFixed(1)}</span>
						</a>
					{/each}
				</div>

				{#if total > perPage}
					<div class="pagination">
						<button class="btn" disabled={currentPage === 0} onclick={() => { currentPage--; load(); }}>Previous</button>
						<span class="page-info">Page {currentPage + 1} of {Math.ceil(total / perPage)}</span>
						<button class="btn" disabled={(currentPage + 1) * perPage >= total} onclick={() => { currentPage++; load(); }}>Next</button>
					</div>
				{/if}
			{/if}
		</div>
	{/if}
</div>

<style>
	.search-row { display: flex; gap: 0.625rem; }
	.search-row .search-input { flex: 1; }

	.results { display: flex; flex-direction: column; }
	.result-row {
		display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem 0;
		border-bottom: 1px solid var(--color-border); color: var(--color-text); font-size: 0.85rem;
	}
	.result-row:last-child { border-bottom: none; }
	.result-row:hover { text-decoration: none; background: var(--color-bg); }
	.occ-code { flex: 0 0 50px; font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace; font-weight: 600; color: var(--color-accent); font-size: 0.8125rem; }
	.occ-title { flex: 1; }
	.skill-name { flex: 0 0 150px; color: var(--color-text-secondary); font-size: 0.8rem; }
	.bar-wrap { flex: 0 0 80px; height: 8px; background: var(--color-border); border-radius: 4px; overflow: hidden; }
	.bar-fill { height: 100%; background: var(--color-accent); border-radius: 4px; }
	.val { flex: 0 0 30px; text-align: right; font-size: 0.8rem; color: var(--color-text-secondary); }
	.no-results { color: var(--color-text-secondary); text-align: center; padding: 2rem; }

	.pagination { display: flex; align-items: center; justify-content: center; gap: 1rem; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--color-border); }
	.page-info { font-size: 0.85rem; color: var(--color-text-secondary); }
</style>

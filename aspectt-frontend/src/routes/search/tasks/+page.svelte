<script lang="ts">
	import { searchTasks, type TaskResult } from '$lib/api/client';

	let query = $state('');
	let results = $state<TaskResult[]>([]);
	let total = $state(0);
	let loading = $state(false);
	let searched = $state(false);
	let currentPage = $state(0);
	const perPage = 50;

	async function doSearch() {
		if (!query.trim()) return;
		loading = true;
		searched = true;
		currentPage = 0;
		await load();
	}

	async function load() {
		loading = true;
		const data = await searchTasks(query, perPage, currentPage * perPage);
		results = data.results;
		total = data.total;
		loading = false;
	}

	function onKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') doSearch();
	}
</script>

<svelte:head><title>Job duties search - ASPECTT</title></svelte:head>

<div class="container">
	<h1 class="page-title">Job duties search</h1>
	<p class="page-desc">Search across task statements for all occupations.</p>

	<div class="card">
		<div class="search-row">
			<input class="search-input" type="text" placeholder="e.g. software testing, patient care, financial analysis..."
				bind:value={query} onkeydown={onKeydown} />
			<button class="btn btn-primary" onclick={doSearch}>Search</button>
		</div>
	</div>

	{#if loading}
		<div class="loading"><div class="spinner"></div></div>
	{:else if searched}
		<div class="card">
			<h2>Results ({total} matching tasks)</h2>
			{#if results.length === 0}
				<p class="no-results">No tasks found matching "{query}"</p>
			{:else}
				<div class="results">
					{#each results as r}
						<div class="result-item">
							<a href="/occupation/{r.uk_soc_2020}" class="result-occ">
								<span class="occ-code">{r.uk_soc_2020}</span>
								<span class="occ-title">{r.title}</span>
							</a>
							<p class="task-text">
								{#if r.task_type === 'Core'}<span class="badge">Core</span>{/if}
								{r.task}
							</p>
						</div>
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
	.page-title { font-size: 1.75rem; color: var(--color-text); margin-bottom: 0.25rem; }
	.page-desc { color: var(--color-text-secondary); margin-bottom: 1.5rem; }

	.search-row { display: flex; gap: 0.75rem; }
	.search-row .search-input { flex: 1; }

	.results { display: flex; flex-direction: column; gap: 0.75rem; }
	.result-item { padding: 0.75rem 0; border-bottom: 1px solid var(--color-border); }
	.result-item:last-child { border-bottom: none; }
	.result-occ { display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.25rem; }
	.occ-code { font-family: monospace; font-weight: 700; color: var(--color-accent); }
	.occ-title { font-weight: 600; font-size: 0.9rem; }
	.task-text { font-size: 0.85rem; color: var(--color-text-secondary); line-height: 1.5; }
	.no-results { color: var(--color-text-secondary); text-align: center; padding: 2rem; }

	.pagination { display: flex; align-items: center; justify-content: center; gap: 1rem; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--color-border); }
	.page-info { font-size: 0.85rem; color: var(--color-text-secondary); }
</style>

<script lang="ts">
	import { listOccupations, type Occupation } from '$lib/api/client';

	let occupations = $state<Occupation[]>([]);
	let total = $state(0);
	let loading = $state(true);
	let query = $state('');
	let jobZoneFilter = $state<number | undefined>(undefined);
	let majorGroupFilter = $state<number | undefined>(undefined);
	let currentPage = $state(0);
	const perPage = 100;

	const majorGroups: Record<number, string> = {
		1: 'Managers, Directors & Senior Officials',
		2: 'Professional Occupations',
		3: 'Associate Professional Occupations',
		4: 'Administrative & Secretarial',
		5: 'Skilled Trades',
		6: 'Caring, Leisure & Other Service',
		7: 'Sales & Customer Service',
		8: 'Process, Plant & Machine Operatives',
		9: 'Elementary Occupations',
	};

	async function load() {
		loading = true;
		const data = await listOccupations({
			q: query || undefined,
			majorGroup: majorGroupFilter,
			jobZone: jobZoneFilter,
			limit: perPage,
			offset: currentPage * perPage,
		});
		occupations = data.occupations;
		total = data.total;
		loading = false;
	}

	$effect(() => {
		// Re-trigger on filter changes
		void [query, jobZoneFilter, majorGroupFilter, currentPage];
		load();
	});

	function resetFilters() {
		query = '';
		jobZoneFilter = undefined;
		majorGroupFilter = undefined;
		currentPage = 0;
	}
</script>

<svelte:head><title>All occupations - ASPECTT</title></svelte:head>

<div class="container">
	<h1 class="page-title">All occupations</h1>
	<p class="page-desc">Browse all {total} UK SOC 2020 occupations with filtering options.</p>

	<div class="card filters">
		<div class="filter-row">
			<input class="search-input filter-search" type="text" placeholder="Filter by title or code..."
				bind:value={query} oninput={() => currentPage = 0} />
			<select bind:value={majorGroupFilter} onchange={() => currentPage = 0} class="filter-select">
				<option value={undefined}>All major groups</option>
				{#each Object.entries(majorGroups) as [code, name]}
					<option value={Number(code)}>{code} - {name}</option>
				{/each}
			</select>
			<select bind:value={jobZoneFilter} onchange={() => currentPage = 0} class="filter-select">
				<option value={undefined}>All job zones</option>
				<option value={2}>Zone 2</option>
				<option value={3}>Zone 3</option>
				<option value={4}>Zone 4</option>
				<option value={5}>Zone 5</option>
			</select>
			<button class="btn" onclick={resetFilters}>Reset</button>
		</div>
		<p class="result-count">{total} occupations found</p>
	</div>

	{#if loading}
		<div class="loading"><div class="spinner"></div></div>
	{:else}
		<div class="card">
			<div class="occ-table">
				<div class="table-header">
					<span class="col-code">SOC Code</span>
					<span class="col-title">Title</span>
				</div>
				{#each occupations as occ}
					<a href="/occupation/{occ.uk_soc_2020}" class="table-row">
						<span class="col-code">{occ.uk_soc_2020}</span>
						<span class="col-title">{occ.title}</span>
					</a>
				{/each}
			</div>

			{#if total > perPage}
				<div class="pagination">
					<button class="btn" disabled={currentPage === 0} onclick={() => currentPage--}>Previous</button>
					<span class="page-info">
						Page {currentPage + 1} of {Math.ceil(total / perPage)}
					</span>
					<button class="btn" disabled={(currentPage + 1) * perPage >= total} onclick={() => currentPage++}>Next</button>
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.filters { margin-bottom: 1rem; }
	.filter-row { display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: center; }
	.filter-search { flex: 1; min-width: 200px; }
	.filter-select { padding: 0.5rem; border: 1px solid var(--color-border); border-radius: var(--radius); font-size: 0.85rem; font-family: var(--font); transition: border-color var(--transition); }
	.filter-select:focus { border-color: var(--color-accent); outline: none; }
	.result-count { font-size: 0.8125rem; color: var(--color-text-secondary); margin-top: 0.5rem; }

	.occ-table { display: flex; flex-direction: column; }
	.table-header { display: flex; gap: 1rem; padding: 0.5rem 0; border-bottom: 2px solid var(--color-border); font-weight: 600; font-size: 0.75rem; color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 0.04em; }
	.table-row { display: flex; gap: 1rem; padding: 0.5625rem 0; border-bottom: 1px solid var(--color-border); color: var(--color-text); font-size: 0.875rem; transition: background var(--transition); }
	.table-row:hover { background: var(--color-bg); color: var(--color-accent); text-decoration: none; }
	.col-code { flex: 0 0 80px; font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace; font-weight: 600; font-size: 0.8125rem; }
	.table-row .col-code { color: var(--color-accent); }
	.col-title { flex: 1; }

	.pagination { display: flex; align-items: center; justify-content: center; gap: 1rem; margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid var(--color-border); }
	.page-info { font-size: 0.8125rem; color: var(--color-text-secondary); }
</style>

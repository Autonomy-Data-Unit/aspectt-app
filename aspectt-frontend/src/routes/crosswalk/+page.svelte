<script lang="ts">
	import { getCrosswalk, searchOccupations, type Occupation } from '$lib/api/client';

	let ukSocFilter = $state('');
	let onetSocFilter = $state('');
	let results = $state<Array<{ onet_soc: string; onet_title: string; uk_soc_2020: number; uk_soc_title: string; weight: number }>>([]);
	let total = $state(0);
	let loading = $state(false);
	let currentPage = $state(0);
	const perPage = 50;

	let ukSuggestions = $state<Occupation[]>([]);
	let ukSearchTimeout: ReturnType<typeof setTimeout>;

	function onUkSocInput() {
		clearTimeout(ukSearchTimeout);
		if (ukSocFilter.trim().length < 1) { ukSuggestions = []; return; }
		ukSearchTimeout = setTimeout(async () => {
			const data = await searchOccupations(ukSocFilter, 8);
			ukSuggestions = data.occupations;
		}, 200);
	}

	function onUkSocKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') ukSuggestions = [];
	}

	function onUkSocBlur() {
		// Delay to allow click on suggestion to fire first
		setTimeout(() => { ukSuggestions = []; }, 150);
	}

	function selectUkSoc(occ: Occupation) {
		ukSocFilter = String(occ.uk_soc_2020);
		ukSuggestions = [];
	}

	async function search() {
		ukSuggestions = [];
		loading = true;
		currentPage = 0;
		await load();
	}

	async function load() {
		loading = true;
		const data = await getCrosswalk({
			ukSoc: ukSocFilter ? Number(ukSocFilter) : undefined,
			onetSoc: onetSocFilter || undefined,
			limit: perPage,
			offset: currentPage * perPage,
		});
		results = data.crosswalk;
		total = data.total;
		loading = false;
	}

	function reset() {
		ukSocFilter = '';
		onetSocFilter = '';
		results = [];
		total = 0;
		currentPage = 0;
		ukSuggestions = [];
	}
</script>

<svelte:head><title>SOC Crosswalk - ASPECTT</title></svelte:head>

<div class="container">
	<h1 class="page-title">US O*NET to UK SOC crosswalk</h1>
	<p class="page-desc">
		The mapping between US O*NET SOC codes and UK SOC 2020 codes.
		Each UK occupation may draw on several US O*NET occupations, weighted by relevance.
	</p>

	<div class="card">
		<h2>Search crosswalk</h2>
		<div class="filter-row">
			<div class="filter-group filter-group-suggest">
				<label for="uk-soc-input">UK SOC 2020 code</label>
				<input id="uk-soc-input" type="text" class="search-input filter-input" placeholder="e.g. 2134 or title..." bind:value={ukSocFilter} oninput={onUkSocInput} onkeydown={onUkSocKeydown} onblur={onUkSocBlur} />
				{#if ukSuggestions.length > 0}
					<div class="suggest-dropdown">
						{#each ukSuggestions as occ}
							<button class="suggest-item" onclick={() => selectUkSoc(occ)}>
								<span class="suggest-code">{occ.uk_soc_2020}</span> {occ.title}
							</button>
						{/each}
					</div>
				{/if}
			</div>
			<div class="filter-group">
				<label for="onet-soc-input">O*NET SOC code</label>
				<input id="onet-soc-input" type="text" class="search-input filter-input" placeholder="e.g. 15-1252.00" bind:value={onetSocFilter} />
			</div>
			<div class="filter-actions">
				<button class="btn btn-primary" onclick={search}>Search</button>
				<button class="btn" onclick={reset}>Reset</button>
			</div>
		</div>
	</div>

	{#if loading}
		<div class="loading"><div class="spinner"></div></div>
	{:else if results.length > 0}
		<div class="card">
			<h2>Results ({total} mappings)</h2>
			<div class="xw-table">
				<div class="xw-header">
					<span class="col-onet">O*NET SOC</span>
					<span class="col-onet-title">O*NET Title</span>
					<span class="col-uk">UK SOC</span>
					<span class="col-uk-title">UK Title</span>
					<span class="col-weight">Weight</span>
				</div>
				{#each results as row}
					<div class="xw-row">
						<span class="col-onet mono">{row.onet_soc}</span>
						<span class="col-onet-title">{row.onet_title}</span>
						<a href="/occupation/{row.uk_soc_2020}" class="col-uk mono">{row.uk_soc_2020}</a>
						<span class="col-uk-title">{row.uk_soc_title}</span>
						<span class="col-weight">{row.weight.toFixed(3)}</span>
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
		</div>
	{/if}
</div>

<style>
	.filter-row { display: flex; gap: 1rem; flex-wrap: wrap; align-items: flex-end; }
	.filter-group { display: flex; flex-direction: column; gap: 0.375rem; }
	.filter-group-suggest { position: relative; }
	.filter-group label { font-size: 0.75rem; font-weight: 600; color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }
	.filter-input { width: 260px; }
	.filter-actions { display: flex; gap: 0.5rem; align-items: flex-end; padding-bottom: 1px; }

	.suggest-dropdown {
		position: absolute; top: 100%; left: 0; z-index: 10;
		background: var(--color-surface); border: 1px solid var(--color-border);
		border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); max-height: 260px; overflow-y: auto;
		min-width: 260px; width: max-content; max-width: 450px; margin-top: 0.375rem;
		animation: fade-in 0.15s ease-out;
	}
	@keyframes fade-in { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }
	.suggest-item {
		display: block; width: 100%; padding: 0.5625rem 1rem; background: none; border: none;
		text-align: left; font-size: 0.8125rem; cursor: pointer; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
		font-family: var(--font); transition: background var(--transition);
	}
	.suggest-item:hover { background: var(--color-bg); }
	.suggest-code { font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace; font-weight: 600; color: var(--color-accent); margin-right: 0.5rem; font-size: 0.8125rem; }

	.xw-table { font-size: 0.8125rem; }
	.xw-header { display: flex; gap: 0.5rem; padding: 0.5rem 0; border-bottom: 2px solid var(--color-border); font-weight: 600; color: var(--color-text-secondary); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; }
	.xw-row { display: flex; gap: 0.5rem; padding: 0.5rem 0; border-bottom: 1px solid var(--color-border); align-items: center; transition: background var(--transition); }
	.xw-row:hover { background: var(--color-bg); }
	.col-onet { flex: 0 0 110px; }
	.col-onet-title { flex: 1; }
	.col-uk { flex: 0 0 70px; }
	.col-uk-title { flex: 1; }
	.col-weight { flex: 0 0 60px; text-align: right; }
	.mono { font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace; font-weight: 600; color: var(--color-accent); font-size: 0.8125rem; }

	.pagination { display: flex; align-items: center; justify-content: center; gap: 1rem; margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid var(--color-border); }
	.page-info { font-size: 0.8125rem; color: var(--color-text-secondary); }
</style>

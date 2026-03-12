<script lang="ts">
	import { getInterests, type InterestSummary, type OccupationWithZone } from '$lib/api/client';

	let interests = $state<InterestSummary[]>([]);
	let loading = $state(true);
	let selectedCodes = $state<string[]>([]);
	let occupations = $state<OccupationWithZone[]>([]);
	let resultTotal = $state(0);
	let searching = $state(false);
	let jobZoneFilter = $state<number | undefined>(undefined);

	const RIASEC_DESCRIPTIONS: Record<string, string> = {
		Realistic: 'People who have athletic or mechanical ability, prefer to work with objects, machines, tools, plants or animals, or to be outdoors.',
		Investigative: 'People who like to observe, learn, investigate, analyse, evaluate or solve problems.',
		Artistic: 'People who have artistic, innovating or intuitional abilities, and like to work in unstructured situations, using their imagination or creativity.',
		Social: 'People who like to work with people to inform, enlighten, help, train, develop, or cure them, or are skilled with words.',
		Enterprising: 'People who like to work with people to influence, persuade, perform, lead or manage for organisational goals or for economic gain.',
		Conventional: 'People who like to work with data, have clerical or numerical ability, carrying things out in detail or following through on others\' instructions.',
	};

	const RIASEC_COLORS: Record<string, string> = {
		R: '#e53e3e', I: '#3182ce', A: '#805ad5', S: '#38a169', E: '#d69e2e', C: '#718096',
	};

	$effect(() => {
		getInterests().then((data) => {
			interests = data.interests;
			loading = false;
		});
	});

	function toggleCode(letter: string) {
		if (selectedCodes.includes(letter)) {
			selectedCodes = selectedCodes.filter(c => c !== letter);
		} else if (selectedCodes.length < 3) {
			selectedCodes = [...selectedCodes, letter];
		}
	}

	async function search() {
		if (selectedCodes.length === 0) return;
		searching = true;
		const code = selectedCodes.join('');
		const data = await getInterests(code, jobZoneFilter);
		occupations = data.occupations ?? [];
		resultTotal = data.total ?? 0;
		searching = false;
	}

	function clearSelection() {
		selectedCodes = [];
		occupations = [];
		resultTotal = 0;
	}
</script>

<svelte:head><title>Browse by interests - ASPECTT</title></svelte:head>

<div class="container">
	<h1 class="page-title">Browse by interests (RIASEC)</h1>
	<p class="page-desc">
		The <a href="https://en.wikipedia.org/wiki/Holland_Codes" target="_blank" rel="noopener">RIASEC model</a> classifies occupations into six interest types. Select up to three to filter occupations.
		Note: these interests are sourced from interviews with US workers and do not reflect UK workers' perspectives,
		although there may of course be overlap.
	</p>

	{#if loading}
		<div class="loading"><div class="spinner"></div></div>
	{:else}
		<div class="interest-grid">
			{#each interests as interest}
				{@const selected = selectedCodes.includes(interest.code)}
				{@const fullName = Object.keys(RIASEC_DESCRIPTIONS).find(n => n[0] === interest.code) ?? interest.name}
				<button
					class="interest-card"
					class:selected
					style="--interest-color: {RIASEC_COLORS[interest.code]}"
					onclick={() => toggleCode(interest.code)}
				>
					<div class="interest-letter">{interest.code}</div>
					<div class="interest-info">
						<h3>{fullName}</h3>
						<p class="interest-desc">{RIASEC_DESCRIPTIONS[fullName] ?? ''}</p>
						<p class="interest-count">{interest.primary_count} primary occupations</p>
					</div>
				</button>
			{/each}
		</div>

		{#if selectedCodes.length > 0}
			<div class="card search-panel">
				<div class="selection-row">
					<div class="selected-codes">
						<strong>Selected:</strong>
						{#each selectedCodes as code}
							<span class="code-tag" style="background: {RIASEC_COLORS[code]}">{code}</span>
						{/each}
						<span class="code-label">
							({selectedCodes.map(c => interests.find(i => i.code === c)?.name).join(' + ')})
						</span>
					</div>
					<div class="action-row">
						<select bind:value={jobZoneFilter} onchange={search} class="jz-select">
							<option value={undefined}>All job zones</option>
							<option value={2}>Zone 1–2 - Little to Some</option>
							<option value={3}>Zone 3 - Medium</option>
							<option value={4}>Zone 4 - Considerable</option>
							<option value={5}>Zone 5 - Extensive</option>
						</select>
						<button class="btn btn-primary" onclick={search}>
							Find Occupations
						</button>
						<button class="btn" onclick={clearSelection}>Clear</button>
					</div>
				</div>
			</div>
		{/if}

		{#if searching}
			<div class="loading"><div class="spinner"></div></div>
		{:else if occupations.length > 0}
			<div class="card">
				<h2>Matching Occupations ({resultTotal})</h2>
				<div class="results-list">
					{#each occupations as occ}
						<a href="/occupation/{occ.uk_soc_2020}" class="result-item">
							<span class="occ-code">{occ.uk_soc_2020}</span>
							<span class="occ-title">{occ.title}</span>
							{#if occ.riasec_code}
								<span class="riasec-tag">{occ.riasec_code}</span>
							{/if}
							{#if occ.job_zone}
								<span class="jz-tag">JZ{occ.job_zone <= 2 ? '1–2' : occ.job_zone}</span>
							{/if}
						</a>
					{/each}
				</div>
			</div>
		{:else if selectedCodes.length > 0 && resultTotal === 0 && !searching}
			<!-- show nothing until they click Find -->
		{/if}
	{/if}
</div>

<style>
	.page-desc { max-width: 700px; }

	.interest-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 0.875rem; margin-bottom: 1.75rem; }

	.interest-card {
		display: flex; gap: 1rem; padding: 1.125rem; background: var(--color-surface);
		border: 1px solid var(--color-border); border-radius: var(--radius-lg);
		cursor: pointer; text-align: left; transition: all var(--transition);
		box-shadow: var(--shadow-xs); font-family: var(--font);
	}
	.interest-card:hover { border-color: var(--interest-color); }
	.interest-card.selected { border-color: var(--interest-color); background: color-mix(in srgb, var(--interest-color) 5%, white); }

	.interest-letter {
		flex-shrink: 0; width: 48px; height: 48px;
		display: flex; align-items: center; justify-content: center;
		border-radius: 50%; background: var(--interest-color); color: white;
		font-size: 1.25rem; font-weight: 800;
	}
	.interest-info h3 { font-size: 1rem; color: var(--color-primary); margin-bottom: 0.25rem; }
	.interest-desc { font-size: 0.8rem; color: var(--color-text-secondary); line-height: 1.4; }
	.interest-count { font-size: 0.75rem; color: var(--color-text-secondary); margin-top: 0.25rem; font-weight: 600; }

	.search-panel { margin-bottom: 1rem; }
	.selection-row { display: flex; flex-direction: column; gap: 0.75rem; }
	.selected-codes { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
	.code-tag { padding: 0.2rem 0.6rem; border-radius: 12px; color: white; font-weight: 700; font-size: 0.85rem; }
	.code-label { font-size: 0.85rem; color: var(--color-text-secondary); }
	.action-row { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }
	.jz-select { padding: 0.4rem 0.6rem; border: 1px solid var(--color-border); border-radius: var(--radius); font-size: 0.85rem; }

	.results-list { display: flex; flex-direction: column; }
	.result-item {
		display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem 0;
		border-bottom: 1px solid var(--color-border); color: var(--color-text); font-size: 0.9rem;
	}
	.result-item:last-child { border-bottom: none; }
	.result-item:hover { color: var(--color-accent); text-decoration: none; }
	.occ-code { font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace; font-weight: 600; color: var(--color-accent); flex: 0 0 50px; font-size: 0.8125rem; }
	.occ-title { flex: 1; }
	.riasec-tag { font-size: 0.75rem; font-weight: 700; color: var(--color-accent); font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace; }
	.jz-tag { font-size: 0.7rem; padding: 0.1rem 0.4rem; background: var(--color-bg); border-radius: 4px; color: var(--color-text-secondary); }
</style>

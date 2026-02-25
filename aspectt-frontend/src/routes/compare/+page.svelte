<script lang="ts">
	import { searchOccupations, compareOccupations, type Occupation, type CompareOccupation } from '$lib/api/client';

	let searchQuery = $state('');
	let searchResults = $state<Occupation[]>([]);
	let selectedCodes = $state<number[]>([]);
	let comparison = $state<CompareOccupation[]>([]);
	let loading = $state(false);
	let searching = $state(false);
	let searchTimeout: ReturnType<typeof setTimeout>;

	const RIASEC_NAMES: Record<string, string> = { R: 'Realistic', I: 'Investigative', A: 'Artistic', S: 'Social', E: 'Enterprising', C: 'Conventional' };

	function onSearchInput() {
		clearTimeout(searchTimeout);
		if (searchQuery.trim().length < 1) { searchResults = []; return; }
		searchTimeout = setTimeout(async () => {
			searching = true;
			const data = await searchOccupations(searchQuery, 10);
			searchResults = data.occupations.filter(o => !selectedCodes.includes(o.uk_soc_2020));
			searching = false;
		}, 200);
	}

	function onSearchKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') searchResults = [];
	}

	function onSearchBlur() {
		setTimeout(() => { searchResults = []; }, 150);
	}

	function addOccupation(occ: Occupation) {
		if (selectedCodes.length >= 4) return;
		selectedCodes = [...selectedCodes, occ.uk_soc_2020];
		searchQuery = '';
		searchResults = [];
	}

	function removeOccupation(code: number) {
		selectedCodes = selectedCodes.filter(c => c !== code);
		comparison = comparison.filter(c => c.uk_soc_2020 !== code);
	}

	async function doCompare() {
		if (selectedCodes.length < 2) return;
		loading = true;
		const data = await compareOccupations(selectedCodes);
		comparison = data.occupations;
		loading = false;
	}
</script>

<svelte:head><title>Compare Occupations - ASPECTT</title></svelte:head>

<div class="container">
	<h1 class="page-title">Compare Occupations</h1>
	<p class="page-desc">Select 2 to 4 occupations to compare side by side.</p>

	<div class="card">
		<h2>Select Occupations</h2>
		<div class="search-area">
			<input
				class="search-input"
				type="text"
				placeholder="Search for an occupation to add..."
				bind:value={searchQuery}
				oninput={onSearchInput}
				onkeydown={onSearchKeydown}
				onblur={onSearchBlur}
				disabled={selectedCodes.length >= 4}
			/>
			{#if searchResults.length > 0}
				<div class="search-dropdown">
					{#each searchResults as occ}
						<button class="dropdown-item" onclick={() => addOccupation(occ)}>
							<span class="dd-code">{occ.uk_soc_2020}</span> {occ.title}
						</button>
					{/each}
				</div>
			{/if}
		</div>

		{#if selectedCodes.length > 0}
			<div class="selected-list">
				{#each selectedCodes as code, i}
					{@const occ = comparison.find(c => c.uk_soc_2020 === code)}
					<div class="selected-tag">
						<span class="tag-num">{i + 1}</span>
						<span>{code} {occ?.title ?? ''}</span>
						<button class="tag-remove" onclick={() => removeOccupation(code)}>&times;</button>
					</div>
				{/each}
			</div>
			<button class="btn btn-primary" onclick={doCompare} disabled={selectedCodes.length < 2 || loading}>
				{loading ? 'Comparing...' : `Compare ${selectedCodes.length} Occupations`}
			</button>
		{/if}
	</div>

	{#if comparison.length >= 2}
		<div class="compare-grid" style="--cols: {comparison.length}">
			<!-- Header row -->
			<div class="compare-section">
				<div class="section-label"></div>
				{#each comparison as occ}
					<div class="compare-cell header-cell">
						<a href="/occupation/{occ.uk_soc_2020}" class="comp-code">{occ.uk_soc_2020}</a>
						<h3>{occ.title}</h3>
						{#if occ.riasec_code}<span class="badge">{occ.riasec_code}</span>{/if}
						{#if occ.job_zone}<span class="jz-badge">Job Zone {occ.job_zone}</span>{/if}
					</div>
				{/each}
			</div>

			<!-- Description -->
			<div class="compare-section">
				<div class="section-label">Description</div>
				{#each comparison as occ}
					<div class="compare-cell"><p class="desc-text">{occ.description?.slice(0, 200)}{occ.description?.length > 200 ? '...' : ''}</p></div>
				{/each}
			</div>

			<!-- Top Skills -->
			<div class="compare-section">
				<div class="section-label">Top Skills</div>
				{#each comparison as occ}
					<div class="compare-cell">
						{#each occ.top_skills.slice(0, 5) as skill}
							<div class="mini-bar-row">
								<span class="mini-label">{skill.element_name}</span>
								<div class="mini-bar"><div class="mini-fill" style="width: {((skill.value_IM ?? 0) / 5) * 100}%"></div></div>
								<span class="mini-val">{skill.value_IM?.toFixed(1)}</span>
							</div>
						{/each}
					</div>
				{/each}
			</div>

			<!-- Top Knowledge -->
			<div class="compare-section">
				<div class="section-label">Top Knowledge</div>
				{#each comparison as occ}
					<div class="compare-cell">
						{#each occ.top_knowledge.slice(0, 5) as k}
							<div class="mini-bar-row">
								<span class="mini-label">{k.element_name}</span>
								<div class="mini-bar"><div class="mini-fill" style="width: {((k.value_IM ?? 0) / 5) * 100}%"></div></div>
								<span class="mini-val">{k.value_IM?.toFixed(1)}</span>
							</div>
						{/each}
					</div>
				{/each}
			</div>

			<!-- Top Abilities -->
			<div class="compare-section">
				<div class="section-label">Top Abilities</div>
				{#each comparison as occ}
					<div class="compare-cell">
						{#each occ.top_abilities.slice(0, 5) as a}
							<div class="mini-bar-row">
								<span class="mini-label">{a.element_name}</span>
								<div class="mini-bar"><div class="mini-fill" style="width: {((a.value_IM ?? 0) / 5) * 100}%"></div></div>
								<span class="mini-val">{a.value_IM?.toFixed(1)}</span>
							</div>
						{/each}
					</div>
				{/each}
			</div>

			<!-- Top Technology -->
			<div class="compare-section">
				<div class="section-label">Top Tech Skills</div>
				{#each comparison as occ}
					<div class="compare-cell">
						<div class="tech-tags">
							{#each occ.top_technology_skills.slice(0, 8) as tech}
								<span class="tech-tag">{tech.name}</span>
							{/each}
						</div>
						<p class="cell-note">{occ.tech_skill_count} total</p>
					</div>
				{/each}
			</div>

			<!-- Tasks -->
			<div class="compare-section">
				<div class="section-label">Tasks</div>
				{#each comparison as occ}
					<div class="compare-cell">
						<p class="cell-note">{occ.task_count} task statements</p>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	.page-title { font-size: 1.75rem; color: var(--color-primary); margin-bottom: 0.25rem; }
	.page-desc { color: var(--color-text-secondary); margin-bottom: 1.5rem; }

	.search-area { position: relative; margin-bottom: 1rem; }
	.search-dropdown {
		position: absolute; top: 100%; left: 0; right: 0; z-index: 10;
		background: var(--color-surface); border: 1px solid var(--color-border);
		border-radius: var(--radius); box-shadow: var(--shadow-md); max-height: 300px; overflow-y: auto;
	}
	.dropdown-item {
		display: block; width: 100%; padding: 0.6rem 1rem; background: none; border: none;
		text-align: left; font-size: 0.9rem; cursor: pointer;
	}
	.dropdown-item:hover { background: var(--color-bg); }
	.dd-code { font-family: monospace; font-weight: 600; color: var(--color-accent); margin-right: 0.5rem; }

	.selected-list { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }
	.selected-tag {
		display: flex; align-items: center; gap: 0.5rem;
		padding: 0.4rem 0.75rem; background: #ebf4ff; border-radius: 20px; font-size: 0.85rem;
	}
	.tag-num { font-weight: 700; color: var(--color-accent); }
	.tag-remove { background: none; border: none; cursor: pointer; font-size: 1.1rem; color: var(--color-text-secondary); padding: 0 0.25rem; }
	.tag-remove:hover { color: #e53e3e; }

	.compare-grid { margin-top: 1.5rem; }
	.compare-section {
		display: grid; grid-template-columns: 140px repeat(var(--cols), 1fr); gap: 1px;
		background: var(--color-border); margin-bottom: 1px;
	}
	.section-label {
		background: var(--color-primary); color: white; padding: 0.75rem;
		font-size: 0.8rem; font-weight: 700; display: flex; align-items: center;
	}
	.compare-cell {
		background: var(--color-surface); padding: 0.75rem;
	}
	.header-cell { text-align: center; }
	.header-cell h3 { font-size: 0.95rem; color: var(--color-primary); margin: 0.25rem 0; }
	.comp-code { font-family: monospace; font-weight: 700; font-size: 1.1rem; }
	.jz-badge { font-size: 0.7rem; padding: 0.15rem 0.5rem; background: var(--color-bg); border-radius: 12px; display: inline-block; margin-top: 0.25rem; }
	.desc-text { font-size: 0.8rem; color: var(--color-text-secondary); line-height: 1.4; }

	.mini-bar-row { display: flex; align-items: center; gap: 0.35rem; margin-bottom: 0.25rem; }
	.mini-label { flex: 0 0 120px; font-size: 0.75rem; text-align: right; color: var(--color-text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.mini-bar { flex: 1; height: 6px; background: var(--color-border); border-radius: 3px; overflow: hidden; }
	.mini-fill { height: 100%; background: var(--color-accent); border-radius: 3px; }
	.mini-val { flex: 0 0 25px; font-size: 0.7rem; color: var(--color-text-secondary); }

	.tech-tags { display: flex; flex-wrap: wrap; gap: 0.25rem; }
	.tech-tag { padding: 0.15rem 0.4rem; background: var(--color-bg); border: 1px solid var(--color-border); border-radius: 12px; font-size: 0.7rem; }
	.cell-note { font-size: 0.75rem; color: var(--color-text-secondary); margin-top: 0.25rem; }

	@media (max-width: 768px) {
		.compare-section { grid-template-columns: 1fr; }
		.section-label { display: none; }
	}
</style>

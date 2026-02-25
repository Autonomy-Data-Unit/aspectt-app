<script lang="ts">
	import { page } from '$app/state';
	import { getOccupation, type OccupationDetail } from '$lib/api/client';
	import RatedBars from '$lib/components/RatedBars.svelte';

	let occ = $state<OccupationDetail | null>(null);
	let loading = $state(true);
	let error = $state('');
	let activeSection = $state('summary');
	let viewMode = $state<'summary' | 'details'>('summary');

	const sections = [
		{ id: 'summary', label: 'Summary' },
		{ id: 'tasks', label: 'Tasks' },
		{ id: 'skills', label: 'Skills' },
		{ id: 'abilities', label: 'Abilities' },
		{ id: 'knowledge', label: 'Knowledge' },
		{ id: 'technology', label: 'Technology' },
		{ id: 'activities', label: 'Work activities' },
		{ id: 'context', label: 'Work context' },
		{ id: 'styles', label: 'Work styles' },
		{ id: 'interests', label: 'Interests' },
		{ id: 'values', label: 'Work values' },
		{ id: 'education', label: 'Education' },
		{ id: 'related', label: 'Related' },
		{ id: 'sources', label: 'Sources' },
	];

	const RIASEC_NAMES = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional'];

	$effect(() => {
		const code = Number(page.params.code);
		loading = true;
		error = '';
		activeSection = 'summary';
		getOccupation(code)
			.then((data) => { occ = data; loading = false; })
			.catch((e) => { error = e.message; loading = false; });
	});

	function jobZoneLabel(jz: number): string {
		const labels: Record<number, string> = {
			1: 'Little or no preparation needed',
			2: 'Some preparation needed',
			3: 'Medium preparation needed',
			4: 'Considerable preparation needed',
			5: 'Extensive preparation needed',
		};
		return labels[jz] || `Zone ${jz}`;
	}

	function getRiasecCode(): string {
		if (!occ?.interests) return '';
		const sorted = [...occ.interests]
			.filter(i => RIASEC_NAMES.includes(i.element_name))
			.sort((a, b) => ((b as any).value_OI ?? 0) - ((a as any).value_OI ?? 0));
		return sorted.slice(0, 3).map(i => i.element_name[0]).join('');
	}

	function sortedByImportance(items: any[], limit?: number) {
		const sorted = [...items].sort((a, b) => (b.value_IM ?? 0) - (a.value_IM ?? 0));
		return limit ? sorted.slice(0, limit) : sorted;
	}

	function getTopItems<T>(items: T[] | undefined, limit: number): T[] {
		if (!items) return [];
		return viewMode === 'summary' ? items.slice(0, limit) : items;
	}
</script>

<svelte:head>
	{#if occ}<title>{occ.title} - ASPECTT</title>{/if}
</svelte:head>

<div class="container">
	{#if loading}
		<div class="loading"><div class="spinner"></div></div>
	{:else if error}
		<div class="card"><p class="error">{error}</p></div>
	{:else if occ}
		<div class="occ-header">
			<div class="occ-code">{occ.uk_soc_2020}</div>
			<div class="occ-info">
				<h1>{occ.title}</h1>
				<p class="occ-desc">{occ.description}</p>
				<div class="header-tags">
					{#if occ.job_zone}
						<span class="header-tag jz">Job Zone {occ.job_zone}</span>
					{/if}
					{#if getRiasecCode()}
						<span class="header-tag riasec">{getRiasecCode()}</span>
					{/if}
					<button class="header-tag source" onclick={() => activeSection = 'sources'}>{occ.source_occupations?.length ?? 0} source occupations</button>
				</div>
			</div>
		</div>

		<div class="view-toggle">
			<button class="toggle-btn" class:active={viewMode === 'summary'} onclick={() => viewMode = 'summary'}>Summary</button>
			<button class="toggle-btn" class:active={viewMode === 'details'} onclick={() => viewMode = 'details'}>Details</button>
		</div>

		<div class="layout">
			<nav class="sidebar">
				{#each sections as sec}
					<button class="nav-item" class:active={activeSection === sec.id}
						onclick={() => (activeSection = sec.id)}>
						{sec.label}
					</button>
				{/each}
				<hr class="nav-divider" />
				<a href="/compare?code={occ.uk_soc_2020}" class="nav-item compare-link">Compare...</a>
			</nav>

			<div class="content">
				{#if activeSection === 'summary'}
					<div class="card">
						<h2>Overview</h2>
						{#if occ.job_zone}
							<div class="job-zone">
								<strong>Job Zone {occ.job_zone}:</strong> {jobZoneLabel(occ.job_zone)}
							</div>
						{/if}
						{#if occ.alternate_titles?.length}
							<div class="alt-titles">
								<strong>Also known as:</strong>
								{occ.alternate_titles.slice(0, viewMode === 'summary' ? 15 : 50).join(', ')}
								{#if occ.alternate_titles.length > (viewMode === 'summary' ? 15 : 50)}
									<span class="muted">and {occ.alternate_titles.length - (viewMode === 'summary' ? 15 : 50)} more</span>
								{/if}
							</div>
						{/if}
					</div>

					<!-- Quick glance sections in summary mode -->
					{#if occ.skills?.length}
						<div class="card">
							<div class="card-header">
								<h2>Top skills</h2>
								<button class="show-more-btn" onclick={() => activeSection = 'skills'}>View all &rarr;</button>
							</div>
							<RatedBars items={sortedByImportance(occ.skills, 5)} />
						</div>
					{/if}

					{#if occ.knowledge?.length}
						<div class="card">
							<div class="card-header">
								<h2>Top knowledge</h2>
								<button class="show-more-btn" onclick={() => activeSection = 'knowledge'}>View all &rarr;</button>
							</div>
							<RatedBars items={sortedByImportance(occ.knowledge, 5)} />
						</div>
					{/if}

					{#if occ.tasks?.length}
						<div class="card">
							<div class="card-header">
								<h2>Core tasks</h2>
								<button class="show-more-btn" onclick={() => activeSection = 'tasks'}>View all &rarr;</button>
							</div>
							<ul class="task-list">
								{#each occ.tasks.filter(t => t.task_type === 'Core').slice(0, 5) as task}
									<li>{task.task}</li>
								{/each}
							</ul>
						</div>
					{/if}

					{#if occ.technology_skills?.length}
						<div class="card">
							<div class="card-header">
								<h2>Top technology</h2>
								<button class="show-more-btn" onclick={() => activeSection = 'technology'}>View all &rarr;</button>
							</div>
							<div class="tech-grid">
								{#each occ.technology_skills.slice(0, 12) as tech}
									<span class="tech-tag">{tech.name}</span>
								{/each}
							</div>
						</div>
					{/if}

					{#if occ.source_occupations?.length}
						<div class="card">
							<div class="card-header">
								<h2>Source occupations</h2>
								<button class="show-more-btn" onclick={() => activeSection = 'sources'}>View all &rarr;</button>
							</div>
							<p class="muted">Based on {occ.source_occupations.length} US O*NET occupations</p>
							<div class="source-preview">
								{#each occ.source_occupations.slice(0, 3) as src}
									<a class="source-row" href="https://www.onetonline.org/link/summary/{src.onet_soc}" target="_blank" rel="noopener">
										<span class="mono">{src.onet_soc}</span>
										<span class="source-title">{src.onet_title}</span>
									</a>
								{/each}
								{#if occ.source_occupations.length > 3}
									<button class="show-all-btn" onclick={() => activeSection = 'sources'}>
										Show all {occ.source_occupations.length} sources
									</button>
								{/if}
							</div>
						</div>
					{/if}

				{:else if activeSection === 'tasks'}
					<div class="card">
						<h2>Tasks ({occ.tasks?.length ?? 0})</h2>
						{#if occ.tasks?.length}
							{@const tasks = getTopItems(occ.tasks, 30)}
							<div class="task-items">
								{#each tasks as task}
									<div class="task-item">
										<div class="task-content">
											<span class="task-text">{task.task}</span>
											<span class="task-badges">
												{#if task.task_type === 'Core'}<span class="badge">Core</span>{/if}
												{#if task.relevance != null}<span class="relevance-label">{(task.relevance * 100).toFixed(0)}%</span>{/if}
											</span>
										</div>
										{#if task.relevance != null}
											<div class="relevance-track">
												<div class="relevance-fill" style="width: {task.relevance * 100}%"></div>
											</div>
										{/if}
									</div>
								{/each}
							</div>
							{#if viewMode === 'summary' && occ.tasks.length > 30}
								<button class="show-all-btn" onclick={() => viewMode = 'details'}>
									Show all {occ.tasks.length} tasks
								</button>
							{/if}
						{:else}
							<p class="muted">No task data available</p>
						{/if}
					</div>

				{:else if activeSection === 'skills'}
					<div class="card">
						<h2>Skills ({occ.skills?.length ?? 0})</h2>
						{#if occ.skills?.length}
							{@const items = viewMode === 'summary' ? sortedByImportance(occ.skills, 10) : sortedByImportance(occ.skills)}
							<RatedBars {items} />
							{#if viewMode === 'summary' && occ.skills.length > 10}
								<button class="show-all-btn" onclick={() => viewMode = 'details'}>
									Show all {occ.skills.length} skills
								</button>
							{/if}
						{:else}<p class="muted">No skills data available</p>{/if}
					</div>

				{:else if activeSection === 'abilities'}
					<div class="card">
						<h2>Abilities ({occ.abilities?.length ?? 0})</h2>
						{#if occ.abilities?.length}
							{@const items = viewMode === 'summary' ? sortedByImportance(occ.abilities, 10) : sortedByImportance(occ.abilities)}
							<RatedBars {items} />
							{#if viewMode === 'summary' && occ.abilities.length > 10}
								<button class="show-all-btn" onclick={() => viewMode = 'details'}>Show all {occ.abilities.length} abilities</button>
							{/if}
						{:else}<p class="muted">No abilities data available</p>{/if}
					</div>

				{:else if activeSection === 'knowledge'}
					<div class="card">
						<h2>Knowledge ({occ.knowledge?.length ?? 0})</h2>
						{#if occ.knowledge?.length}
							{@const items = viewMode === 'summary' ? sortedByImportance(occ.knowledge, 10) : sortedByImportance(occ.knowledge)}
							<RatedBars {items} />
							{#if viewMode === 'summary' && occ.knowledge.length > 10}
								<button class="show-all-btn" onclick={() => viewMode = 'details'}>Show all {occ.knowledge.length} knowledge areas</button>
							{/if}
						{:else}<p class="muted">No knowledge data available</p>{/if}
					</div>

				{:else if activeSection === 'technology'}
					<div class="card">
						<h2>Technology ({occ.technology_skills?.length ?? 0})</h2>
						{#if occ.technology_skills?.length}
							{@const items = getTopItems(occ.technology_skills, 40)}
							<div class="tech-grid">
								{#each items as tech}
									<span class="tech-tag">{tech.name}</span>
								{/each}
							</div>
							{#if viewMode === 'summary' && occ.technology_skills.length > 40}
								<button class="show-all-btn" onclick={() => viewMode = 'details'}>
									Show all {occ.technology_skills.length} technology skills
								</button>
							{/if}
						{:else}<p class="muted">No technology skills data available</p>{/if}
					</div>

				{:else if activeSection === 'activities'}
					<div class="card">
						<h2>Work activities ({occ.work_activities?.length ?? 0})</h2>
						{#if occ.work_activities?.length}
							{@const items = viewMode === 'summary' ? sortedByImportance(occ.work_activities, 10) : sortedByImportance(occ.work_activities)}
							<RatedBars {items} />
							{#if viewMode === 'summary' && occ.work_activities.length > 10}
								<button class="show-all-btn" onclick={() => viewMode = 'details'}>Show all {occ.work_activities.length} activities</button>
							{/if}
						{:else}<p class="muted">No work activities data available</p>{/if}
					</div>

				{:else if activeSection === 'context'}
					<div class="card">
						<h2>Work context ({occ.work_context?.length ?? 0})</h2>
						{#if occ.work_context?.length}
							{@const items = viewMode === 'summary' ? occ.work_context.slice(0, 10) : occ.work_context}
							<RatedBars {items} />
							{#if viewMode === 'summary' && occ.work_context.length > 10}
								<button class="show-all-btn" onclick={() => viewMode = 'details'}>Show all {occ.work_context.length} context factors</button>
							{/if}
						{:else}<p class="muted">No work context data available</p>{/if}
					</div>

				{:else if activeSection === 'styles'}
					<div class="card">
						<h2>Work styles ({occ.work_styles?.length ?? 0})</h2>
						{#if occ.work_styles?.length}
							<RatedBars items={occ.work_styles} />
						{:else}<p class="muted">No work styles data available</p>{/if}
					</div>

				{:else if activeSection === 'interests'}
					<div class="card">
						<h2>Interests</h2>
						{#if occ.interests?.length}
							{@const riasecItems = occ.interests.filter(i => RIASEC_NAMES.includes(i.element_name))}
							<div class="interest-bars">
								{#each riasecItems.sort((a, b) => ((b as any).value_OI ?? 0) - ((a as any).value_OI ?? 0)) as interest}
									{@const val = (interest as any).value_OI ?? 0}
									<div class="interest-row">
										<span class="interest-code" title={interest.element_name}>{interest.element_name[0]}</span>
										<span class="interest-name">{interest.element_name}</span>
										<div class="interest-bar-track">
											<div class="interest-bar-fill" style="width: {(val / 7) * 100}%"></div>
										</div>
										<span class="interest-val">{val.toFixed(1)}</span>
									</div>
								{/each}
							</div>
							<p class="riasec-label">RIASEC Code: <strong>{getRiasecCode()}</strong></p>
						{:else}<p class="muted">No interests data available</p>{/if}
					</div>

				{:else if activeSection === 'values'}
					<div class="card">
						<h2>Work values</h2>
						{#if occ.work_values?.length}
							{@const valueItems = occ.work_values.filter(v => !v.element_name.includes('High Point'))}
							<div class="interest-bars">
								{#each valueItems.sort((a, b) => ((b as any).value_EX ?? 0) - ((a as any).value_EX ?? 0)) as wv}
									{@const val = (wv as any).value_EX ?? 0}
									<div class="interest-row">
										<span class="interest-name wv-name">{wv.element_name}</span>
										<div class="interest-bar-track">
											<div class="interest-bar-fill wv-fill" style="width: {(val / 7) * 100}%"></div>
										</div>
										<span class="interest-val">{val.toFixed(1)}</span>
									</div>
								{/each}
							</div>
						{:else}<p class="muted">No work values data available</p>{/if}
					</div>

				{:else if activeSection === 'education'}
					<div class="card">
						<h2>Education and training</h2>
						{#if occ.job_zone}
							<div class="job-zone">
								<strong>Job Zone {occ.job_zone}:</strong> {jobZoneLabel(occ.job_zone)}
							</div>
						{/if}
						{#if occ.education?.length}
							<div class="edu-list">
								{#each occ.education as edu}
									<div class="edu-row">
										<span class="edu-label">{edu.Element_Name} (Cat. {edu.Category})</span>
										<div class="bar-track">
											<div class="bar-fill importance" style="width: {Math.min(edu['Data Value'] * 10, 100)}%"></div>
										</div>
										<span class="bar-value">{edu['Data Value'].toFixed(1)}%</span>
									</div>
								{/each}
							</div>
						{:else}<p class="muted">No education data available</p>{/if}
					</div>

				{:else if activeSection === 'related'}
					<div class="card">
						<h2>Related occupations ({occ.related_occupations?.length ?? 0})</h2>
						{#if occ.related_occupations?.length}
							<div class="related-list">
								{#each occ.related_occupations as rel}
									<a class="related-item" href="/occupation/{rel.related_uk_soc}">
										<span class="related-code">{rel.related_uk_soc}</span>
										<span>{rel.related_uk_title}</span>
									</a>
								{/each}
							</div>
						{:else}<p class="muted">No related occupations data available</p>{/if}
					</div>

				{:else if activeSection === 'sources'}
					<div class="card">
						<h2>Source occupations ({occ.source_occupations?.length ?? 0})</h2>
						{#if occ.source_occupations?.length}
							<p class="muted source-intro">The US O*NET occupations whose data contributes to this UK occupation. Click any row to view it on O*NET Online.</p>
							<div class="source-list">
								{#each occ.source_occupations as src}
									{@const pct = src.weight * 100}
									<a class="source-card" href="https://www.onetonline.org/link/summary/{src.onet_soc}" target="_blank" rel="noopener">
										<div class="source-card-top">
											<span class="mono source-code">{src.onet_soc}</span>
											<span class="source-title">{src.onet_title}</span>
											<span class="source-weight">{pct.toFixed(1)}%</span>
										</div>
										<div class="source-bar-track">
											<div class="source-bar-fill" style="width: {pct}%"></div>
										</div>
									</a>
								{/each}
							</div>
						{:else}<p class="muted">No source occupation data available</p>{/if}
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	.occ-header {
		display: flex; gap: 1.75rem; align-items: flex-start; margin-bottom: 1.25rem;
		background: var(--color-surface); padding: 1.75rem; border-radius: var(--radius-lg); border: 1px solid var(--color-border);
		box-shadow: var(--shadow-xs);
	}
	.occ-code {
		font-size: 1.75rem; font-weight: 700; color: var(--color-accent-bright); font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace;
		flex: 0 0 auto; padding: 0.625rem 1.125rem; background: var(--color-accent-subtle); border-radius: var(--radius);
		border: 1px solid rgba(135, 107, 36, 0.1); letter-spacing: -0.02em;
	}
	.occ-info { flex: 1; }
	h1 { font-size: 1.5rem; font-weight: 700; color: var(--color-text); margin-bottom: 0.5rem; letter-spacing: -0.02em; line-height: 1.3; }
	.occ-desc { color: var(--color-text-secondary); font-size: 0.875rem; line-height: 1.6; margin-bottom: 0.625rem; }
	.header-tags { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; }
	.header-tag {
		font-size: 0.6875rem; padding: 0.25rem 0.625rem; border-radius: 5px; font-weight: 600; border: none; font-family: var(--font);
		letter-spacing: 0.02em;
	}
	.header-tag.jz { background: var(--color-primary); color: white; }
	.header-tag.riasec { background: #805ad5; color: white; font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace; letter-spacing: 1px; }
	.header-tag.source { background: var(--color-bg); color: var(--color-text-secondary); cursor: pointer; border: 1px solid var(--color-border); transition: all var(--transition); }
	.header-tag.source:hover { border-color: var(--color-border-hover); background: var(--color-border); }

	.view-toggle { display: flex; gap: 1px; margin-bottom: 1.25rem; background: var(--color-border); border-radius: var(--radius); overflow: hidden; width: fit-content; }
	.toggle-btn {
		padding: 0.4375rem 1rem; border: none; background: var(--color-surface); cursor: pointer;
		font-size: 0.8125rem; font-weight: 500; color: var(--color-text-secondary); transition: all var(--transition); font-family: var(--font);
	}
	.toggle-btn.active { background: var(--color-primary); color: white; }
	.toggle-btn:hover:not(.active) { background: var(--color-bg); }

	.layout { display: grid; grid-template-columns: 175px 1fr; gap: 1.75rem; }
	.sidebar { display: flex; flex-direction: column; gap: 0.125rem; position: sticky; top: 4.5rem; align-self: start; }

	.nav-item {
		display: block; padding: 0.45rem 0.75rem; background: none; border: none;
		border-left: 3px solid transparent; text-align: left; font-size: 0.8125rem;
		color: var(--color-text-secondary); cursor: pointer; border-radius: 0 var(--radius) var(--radius) 0; transition: all var(--transition);
		font-family: var(--font);
	}
	.nav-item:hover { background: var(--color-bg); color: var(--color-text); text-decoration: none; }
	.nav-item.active { border-left-color: var(--color-accent); background: var(--color-accent-subtle); color: var(--color-text); font-weight: 600; }
	.nav-divider { border: none; border-top: 1px solid var(--color-border); margin: 0.25rem 0; }
	.compare-link { color: var(--color-accent); font-size: 0.8rem; }

	.card-header { display: flex; justify-content: space-between; align-items: center; }
	.card-header h2 { flex: 1; }
	.show-more-btn {
		background: none; border: none; color: var(--color-accent); cursor: pointer;
		font-size: 0.85rem; font-weight: 500; padding: 0.25rem 0.5rem;
	}
	.show-more-btn:hover { text-decoration: underline; }
	.show-all-btn {
		display: block; width: 100%; text-align: center; padding: 0.6rem;
		margin-top: 0.75rem; background: var(--color-bg); border: 1px solid var(--color-border);
		border-radius: var(--radius); cursor: pointer; font-size: 0.85rem; color: var(--color-accent);
	}
	.show-all-btn:hover { border-color: var(--color-accent); }

	.job-zone { margin-bottom: 1rem; padding: 0.5rem 0.75rem; background: var(--color-bg); border-radius: var(--radius); font-size: 0.9rem; }
	.alt-titles { margin-bottom: 1rem; font-size: 0.9rem; color: var(--color-text-secondary); line-height: 1.8; }

	.mono { font-family: monospace; font-weight: 600; }
	.muted { color: var(--color-text-secondary); font-size: 0.85rem; }

	/* Source occupations - preview on summary tab */
	.source-preview { display: flex; flex-direction: column; margin-top: 0.5rem; }
	.source-row {
		display: flex; gap: 0.75rem; padding: 0.4rem 0; border-bottom: 1px solid var(--color-border);
		color: var(--color-text); font-size: 0.9rem; align-items: center;
	}
	.source-row:last-child { border-bottom: none; }
	.source-row:hover { color: var(--color-accent); text-decoration: none; }
	.source-row .mono { color: var(--color-accent); flex: 0 0 auto; }
	.source-row .source-title { flex: 1; }

	/* Source occupations - full section */
	.source-intro { margin-bottom: 0.75rem; }
	.source-list { display: flex; flex-direction: column; gap: 0.5rem; }
	.source-card {
		display: block; padding: 0.875rem; border: 1px solid var(--color-border);
		border-radius: var(--radius); color: var(--color-text); transition: all var(--transition);
		box-shadow: var(--shadow-xs);
	}
	.source-card:hover { border-color: var(--color-border-hover); box-shadow: var(--shadow); text-decoration: none; }
	.source-card-top { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.4rem; }
	.source-code { color: var(--color-accent); flex: 0 0 auto; }
	.source-card .source-title { flex: 1; font-size: 0.9rem; }
	.source-weight { flex: 0 0 auto; font-size: 0.85rem; font-weight: 600; color: var(--color-text-secondary); }
	.source-bar-track { height: 6px; background: var(--color-border); border-radius: 3px; overflow: hidden; }
	.source-bar-fill { height: 100%; background: var(--color-accent); border-radius: 3px; transition: width 0.3s; }

	.task-items { display: flex; flex-direction: column; gap: 0.5rem; }
	.task-item { padding: 0.5rem 0; border-bottom: 1px solid var(--color-border); }
	.task-item:last-child { border-bottom: none; }
	.task-content { display: flex; gap: 0.5rem; align-items: flex-start; }
	.task-text { flex: 1; font-size: 0.9rem; line-height: 1.5; overflow-wrap: break-word; }
	.task-badges { flex: 0 0 auto; display: flex; gap: 0.35rem; align-items: center; }
	.relevance-label { font-size: 0.75rem; color: var(--color-text-secondary); font-weight: 500; white-space: nowrap; }
	.relevance-track { height: 3px; background: var(--color-border); border-radius: 2px; overflow: hidden; margin-top: 0.35rem; }
	.relevance-fill { height: 100%; background: var(--color-accent); border-radius: 2px; opacity: 0.6; }

	.tech-grid { display: flex; flex-wrap: wrap; gap: 0.5rem; }
	.tech-tag {
		padding: 0.3rem 0.75rem; background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 20px; font-size: 0.8rem;
		transition: all var(--transition); box-shadow: var(--shadow-xs);
	}
	.tech-tag:hover { border-color: var(--color-border-hover); }

	/* Interest/RIASEC bars */
	.interest-bars { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.5rem; }
	.interest-row { display: flex; align-items: center; gap: 0.75rem; }
	.interest-code {
		flex: 0 0 28px; height: 28px; display: flex; align-items: center; justify-content: center;
		border-radius: 50%; background: var(--color-accent-bright); color: white; font-weight: 800; font-size: 0.85rem;
	}
	.interest-name { flex: 0 0 120px; font-size: 0.85rem; }
	.wv-name { flex: 0 0 160px; }
	.interest-bar-track { flex: 1; height: 18px; background: var(--color-bg); border: 1px solid rgba(0, 0, 0, 0.04); border-radius: 4px; overflow: hidden; }
	.interest-bar-fill { height: 100%; background: #805ad5; border-radius: 3px; transition: width 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94); }
	.wv-fill { background: var(--color-success); }
	.interest-val { flex: 0 0 35px; font-size: 0.85rem; color: var(--color-text-secondary); text-align: right; }
	.riasec-label { margin-top: 0.75rem; font-size: 0.9rem; }

	.edu-list { display: flex; flex-direction: column; gap: 0.3rem; margin-top: 0.5rem; }
	.edu-row { display: flex; align-items: center; gap: 0.75rem; }
	.edu-label { flex: 0 0 220px; font-size: 0.85rem; text-align: right; color: var(--color-text-secondary); }

	.related-list { display: flex; flex-direction: column; }
	.related-item { display: flex; gap: 0.75rem; padding: 0.5rem 0; border-bottom: 1px solid var(--color-border); color: var(--color-text); }
	.related-item:last-child { border-bottom: none; }
	.related-item:hover { color: var(--color-accent); text-decoration: none; }
	.related-code { font-family: monospace; font-weight: 600; color: var(--color-accent); flex: 0 0 50px; }

	.error { color: #e53e3e; text-align: center; padding: 1rem; }

	@media (max-width: 768px) {
		.layout { grid-template-columns: 1fr; }
		.sidebar { flex-direction: row; flex-wrap: wrap; position: static; }
		.nav-item { border-left: none; border-bottom: 2px solid transparent; border-radius: var(--radius); padding: 0.4rem 0.6rem; font-size: 0.8rem; }
		.nav-item.active { border-bottom-color: var(--color-accent); }
		.occ-header { flex-direction: column; }
		.interest-name { flex: 0 0 90px; }
		.edu-label { flex: 0 0 140px; font-size: 0.8rem; }
	}
</style>

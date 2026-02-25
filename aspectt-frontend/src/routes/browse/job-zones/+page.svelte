<script lang="ts">
	import { getJobZones, type JobZone } from '$lib/api/client';

	let zones = $state<JobZone[]>([]);
	let loading = $state(true);
	let expandedZone = $state<number | null>(null);

	$effect(() => {
		getJobZones().then((data) => {
			zones = data.job_zones;
			loading = false;
		});
	});

	const zoneDescriptions: Record<number, string> = {
		1: 'These occupations need little or no preparation. A high school diploma or GED may be required. Little or no previous work-related skill, knowledge, or experience is needed.',
		2: 'These occupations usually need some previous work-related skill, knowledge, or experience. They usually require a secondary education and some vocational training.',
		3: 'These occupations usually need training in vocational schools, on-the-job experience, or an associate\'s degree. Previous work-related skill, knowledge, or experience is required.',
		4: 'Most of these occupations require a four-year bachelor\'s degree, but some do not. Employees in these occupations usually need several years of work-related experience.',
		5: 'These occupations often require graduate school. Extensive skill, knowledge, and experience are needed. Many require more than five years of experience.',
	};
</script>

<svelte:head><title>Browse by job zone - ASPECTT</title></svelte:head>

<div class="container">
	<h1 class="page-title">Browse by job zone</h1>
	<p class="page-desc">
		Job zones group occupations by the level of education, experience and training required.
		There are five zones, from little preparation (zone 1) to extensive preparation (zone 5).
	</p>

	{#if loading}
		<div class="loading"><div class="spinner"></div></div>
	{:else}
		<div class="zones">
			{#each zones as zone}
				<div class="zone-card card">
					<button class="zone-header" onclick={() => expandedZone = expandedZone === zone.zone ? null : zone.zone}>
						<div class="zone-badge">Zone {zone.zone}</div>
						<div class="zone-info">
							<h2>{zone.name}</h2>
							<p class="zone-count">{zone.occupation_count} occupations</p>
						</div>
						<span class="expand-icon">{expandedZone === zone.zone ? '\u25B2' : '\u25BC'}</span>
					</button>
					{#if expandedZone === zone.zone}
						<div class="zone-detail">
							<p class="zone-desc">{zoneDescriptions[zone.zone]}</p>
							<div class="occ-list">
								{#each zone.occupations as occ}
									<a href="/occupation/{occ.uk_soc_2020}" class="occ-item">
										<span class="occ-code">{occ.uk_soc_2020}</span>
										<span>{occ.title}</span>
									</a>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.zones { display: flex; flex-direction: column; gap: 0.875rem; }

	.zone-card { padding: 0; overflow: hidden; }

	.zone-header {
		display: flex; align-items: center; gap: 1rem; padding: 1.25rem 1.5rem;
		background: none; border: none; width: 100%; cursor: pointer; text-align: left;
		font-family: var(--font); transition: background var(--transition);
	}

	.zone-header:hover { background: var(--color-bg); }

	.zone-badge {
		flex-shrink: 0; width: 70px; text-align: center;
		padding: 0.5rem; border-radius: var(--radius);
		background: var(--color-accent); color: white;
		font-weight: 700; font-size: 0.85rem;
	}

	.zone-info { flex: 1; }
	.zone-info h2 { font-size: 1.1rem; color: var(--color-primary); border: none; margin: 0; padding: 0; }
	.zone-count { font-size: 0.8125rem; color: var(--color-text-secondary); }
	.expand-icon { font-size: 0.75rem; color: var(--color-text-secondary); }

	.zone-detail { padding: 0 1.5rem 1.5rem; border-top: 1px solid var(--color-border); }
	.zone-desc { font-size: 0.875rem; color: var(--color-text-secondary); margin: 1rem 0; line-height: 1.6; }

	.occ-list { display: flex; flex-direction: column; }
	.occ-item {
		display: flex; gap: 0.75rem; padding: 0.4375rem 0;
		border-bottom: 1px solid var(--color-border); color: var(--color-text); font-size: 0.875rem;
		transition: color var(--transition);
	}
	.occ-item:last-child { border-bottom: none; }
	.occ-item:hover { color: var(--color-accent); text-decoration: none; }
	.occ-code { font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace; font-weight: 600; color: var(--color-accent); flex: 0 0 50px; font-size: 0.8125rem; }
</style>

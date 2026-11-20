<template>
  <div class="space-y-6">
    <PageHeader
      title="Pendanaan"
      description="Dana hibah penelitian dan pengabdian per prodi, per dosen, per tahun, dan per skema."
      :meta="meta"
    />
    <FundingDashboard />
  </div>
</template>

<script setup>
import { syncLabel } from '../utils/format.js'
import PageHeader from '../components/ui/PageHeader.vue'
import FundingDashboard from '../components/FundingDashboard.vue'

const meta = syncLabel('SINTA')
</script>

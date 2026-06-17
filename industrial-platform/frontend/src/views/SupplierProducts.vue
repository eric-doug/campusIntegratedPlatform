<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>供应商商品管理</span>
          <div>
            <el-tag v-if="supplier" type="success" style="margin-right: 8px">{{ supplier.name }} ({{ supplier.code }})</el-tag>
            <el-button type="primary" @click="openCreateDialog">录入商品</el-button>
          </div>
        </div>
      </template>

      <div style="margin-bottom: 16px; display: flex; gap: 12px">
        <el-input v-model="keyword" placeholder="搜索商品名称/描述" clearable style="width: 240px" @clear="loadProducts" @keyup.enter="loadProducts" />
        <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 140px" @change="loadProducts">
          <el-option label="上架" value="active" />
          <el-option label="下架" value="inactive" />
          <el-option label="已删除" value="deleted" />
        </el-select>
        <el-button type="primary" @click="loadProducts">查询</el-button>
      </div>

      <el-table :data="products" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="商品名称" min-width="180" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="sku_count" label="SKU数" width="80" align="center" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : row.status === 'deleted' ? 'danger' : 'info'">
              {{ statusMap[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="openEditDialog(row)">编辑</el-button>
            <el-button text type="warning" @click="openSkuDialog(row)">追加SKU</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadProducts" />
    </el-card>

    <!-- 录入/编辑商品对话框 -->
    <el-dialog v-model="showProductDialog" :title="editingProduct ? '编辑商品' : '录入商品'" width="720px" :close-on-click-modal="false">
      <el-form :model="productForm" label-width="100px" ref="productFormRef" :rules="productRules">
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="productForm.name" placeholder="请输入商品名称" />
        </el-form-item>
        <el-form-item label="商品分类">
          <el-cascader
            v-model="productForm.categoryCascade"
            :options="categoryTree"
            :props="{ value: 'id', label: 'name', children: 'children', checkStrictly: true, emitPath: false }"
            placeholder="请选择分类"
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="productForm.unit" placeholder="如：个/台/箱" style="width: 200px" />
        </el-form-item>
        <el-form-item label="商品描述">
          <el-input v-model="productForm.description" type="textarea" :rows="3" placeholder="请输入商品描述" />
        </el-form-item>
        <el-form-item label="规格属性">
          <div v-for="(spec, idx) in productForm.specList" :key="idx" style="display: flex; gap: 8px; margin-bottom: 8px; width: 100%">
            <el-input v-model="spec.key" placeholder="属性名(如:颜色)" style="width: 180px" />
            <el-input v-model="spec.value" placeholder="属性值(如:红色)" style="flex: 1" />
            <el-button text type="danger" @click="productForm.specList.splice(idx, 1)">删除</el-button>
          </div>
          <el-button text type="primary" @click="productForm.specList.push({ key: '', value: '' })">+ 添加规格属性</el-button>
        </el-form-item>
      </el-form>

      <!-- SKU 列表（仅新增时显示） -->
      <div v-if="!editingProduct">
        <el-divider content-position="left">SKU 规格信息</el-divider>
        <el-table :data="productForm.skus" border size="small">
          <el-table-column label="SKU编码" min-width="140">
            <template #default="{ row }">
              <el-input v-model="row.sku_code" placeholder="如:SKU-RED-001" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="价格(元)" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.price" :min="0" :precision="2" size="small" controls-position="right" style="width: 100px" />
            </template>
          </el-table-column>
          <el-table-column label="原价(元)" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.original_price" :min="0" :precision="2" size="small" controls-position="right" style="width: 100px" />
            </template>
          </el-table-column>
          <el-table-column label="库存" width="100">
            <template #default="{ row }">
              <el-input-number v-model="row.stock" :min="0" size="small" controls-position="right" style="width: 80px" />
            </template>
          </el-table-column>
          <el-table-column label="起订量" width="100">
            <template #default="{ row }">
              <el-input-number v-model="row.min_order_qty" :min="1" size="small" controls-position="right" style="width: 80px" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" align="center">
            <template #default="{ $index }">
              <el-button text type="danger" size="small" @click="removeSku($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button text type="primary" style="margin-top: 8px" @click="addSkuRow">+ 添加SKU</el-button>
      </div>

      <template #footer>
        <el-button @click="showProductDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveProduct" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 追加 SKU 对话框 -->
    <el-dialog v-model="showSkuDialog" title="追加 SKU 规格" width="560px" :close-on-click-modal="false">
      <el-form :model="skuForm" label-width="100px">
        <el-form-item label="商品名称">
          <el-input :model-value="skuTargetProduct?.name" disabled />
        </el-form-item>
        <el-form-item label="SKU编码" required>
          <el-input v-model="skuForm.sku_code" placeholder="请输入SKU编码" />
        </el-form-item>
        <el-form-item label="价格(元)" required>
          <el-input-number v-model="skuForm.price" :min="0" :precision="2" controls-position="right" />
        </el-form-item>
        <el-form-item label="原价(元)">
          <el-input-number v-model="skuForm.original_price" :min="0" :precision="2" controls-position="right" />
        </el-form-item>
        <el-form-item label="库存">
          <el-input-number v-model="skuForm.stock" :min="0" controls-position="right" />
        </el-form-item>
        <el-form-item label="起订量">
          <el-input-number v-model="skuForm.min_order_qty" :min="1" controls-position="right" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSkuDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddSku" :loading="saving">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMySupplierProfile, getMyProducts, createMyProduct, updateMyProduct, addProductSku } from '@/api/suppliers'
import { getCategories } from '@/api/categories'

const statusMap = { active: '上架', inactive: '下架', deleted: '已删除' }

const supplier = ref(null)
const products = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const keyword = ref('')
const statusFilter = ref('')

const showProductDialog = ref(false)
const showSkuDialog = ref(false)
const saving = ref(false)
const editingProduct = ref(null)
const skuTargetProduct = ref(null)
const categoryTree = ref([])

const productFormRef = ref()
const productRules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
}

const defaultProductForm = () => ({
  name: '',
  categoryCascade: null,
  unit: '',
  description: '',
  specList: [],
  skus: [],
})
const productForm = reactive(defaultProductForm())

const defaultSkuForm = () => ({
  sku_code: '',
  price: 0,
  original_price: null,
  stock: 0,
  min_order_qty: 1,
})
const skuForm = reactive(defaultSkuForm())

const loadSupplier = async () => {
  try {
    const res = await getMySupplierProfile()
    supplier.value = res.data
  } catch (e) {
    // 未关联供应商
    supplier.value = null
  }
}

const loadCategories = async () => {
  try {
    const res = await getCategories()
    categoryTree.value = res.data || []
  } catch (e) {
    categoryTree.value = []
  }
}

const loadProducts = async () => {
  loading.value = true
  try {
    const res = await getMyProducts({ page: page.value, per_page: 20, keyword: keyword.value, status: statusFilter.value })
    products.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  editingProduct.value = null
  Object.assign(productForm, defaultProductForm())
  addSkuRow()
  showProductDialog.value = true
}

const openEditDialog = (row) => {
  editingProduct.value = row
  Object.assign(productForm, {
    name: row.name,
    categoryCascade: row.category_id,
    unit: row.unit,
    description: row.description,
    specList: [],
    skus: [],
  })
  // 解析已有 specs
  if (row.specs && typeof row.specs === 'object') {
    productForm.specList = Object.entries(row.specs).map(([k, v]) => ({ key: k, value: String(v) }))
  }
  showProductDialog.value = true
}

const openSkuDialog = (row) => {
  skuTargetProduct.value = row
  Object.assign(skuForm, defaultSkuForm())
  showSkuDialog.value = true
}

const addSkuRow = () => {
  productForm.skus.push({
    sku_code: '',
    price: 0,
    original_price: null,
    stock: 0,
    min_order_qty: 1,
  })
}

const removeSku = (idx) => {
  productForm.skus.splice(idx, 1)
}

const buildSpecs = () => {
  const specs = {}
  productForm.specList.forEach((s) => {
    if (s.key && s.value) specs[s.key] = s.value
  })
  return specs
}

const handleSaveProduct = async () => {
  await productFormRef.value.validate()
  saving.value = true
  try {
    if (editingProduct.value) {
      // 编辑模式
      await updateMyProduct(editingProduct.value.id, {
        name: productForm.name,
        category_id: productForm.categoryCascade || null,
        unit: productForm.unit,
        description: productForm.description,
        specs: buildSpecs(),
      })
      ElMessage.success('商品更新成功')
    } else {
      // 新增模式
      if (productForm.skus.length === 0) {
        ElMessage.warning('至少需要添加一个SKU')
        return
      }
      await createMyProduct({
        name: productForm.name,
        category_id: productForm.categoryCascade || null,
        unit: productForm.unit,
        description: productForm.description,
        specs: buildSpecs(),
        skus: productForm.skus,
      })
      ElMessage.success('商品录入成功')
    }
    showProductDialog.value = false
    loadProducts()
  } finally {
    saving.value = false
  }
}

const handleAddSku = async () => {
  if (!skuForm.sku_code) {
    ElMessage.warning('请输入SKU编码')
    return
  }
  if (skuForm.price == null) {
    ElMessage.warning('请输入价格')
    return
  }
  saving.value = true
  try {
    await addProductSku(skuTargetProduct.value.id, { ...skuForm })
    ElMessage.success('SKU添加成功')
    showSkuDialog.value = false
    loadProducts()
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await loadSupplier()
  await loadCategories()
  if (supplier.value) {
    loadProducts()
  } else {
    ElMessage.warning('当前用户未关联供应商账号，请联系管理员')
  }
})
</script>

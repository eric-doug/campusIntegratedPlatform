#!/bin/bash
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# 配置
COMPOSE_FILE="docker-compose.yml"
COMPOSE_DEV_FILE="docker-compose.dev.yml"
ENV_FILE=".env"
ENV_EXAMPLE=".env.example"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "校园综合平台部署脚本"
    echo ""
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  start [dev|prod]    启动所有服务 (默认: dev)"
    echo "  stop                停止所有服务"
    echo "  restart [dev|prod]  重启所有服务"
    echo "  status              查看服务状态"
    echo "  logs [服务名]        查看日志 (可选指定服务)"
    echo "  build [dev|prod]    构建镜像"
    echo "  clean               清理所有容器、镜像和数据卷"
    echo "  init                初始化环境（复制 .env 文件）"
    echo "  backup              备份数据库"
    echo "  restore [文件]      恢复数据库"
    echo "  help                显示此帮助信息"
    echo ""
    echo "服务名:"
    echo "  postgres            PostgreSQL 数据库"
    echo "  redis               Redis 缓存"
    echo "  elasticsearch       Elasticsearch 搜索引擎"
    echo "  nginx-gateway       Nginx 网关"
    echo "  industrial-backend  工业平台后端"
    echo "  industrial-frontend 工业平台前端"
    echo "  supply-backend      供应链平台后端"
    echo "  supply-frontend     供应链平台前端"
    echo "  park-backend        园区服务后端"
    echo "  park-frontend       园区服务前端"
    echo ""
    echo "示例:"
    echo "  $0 start dev        # 启动开发环境"
    echo "  $0 start prod       # 启动生产环境"
    echo "  $0 logs industrial-backend  # 查看工业平台后端日志"
    echo "  $0 backup           # 备份数据库"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    print_success "依赖检查通过"
}

# 获取 docker-compose 命令
get_compose_cmd() {
    if docker compose version &> /dev/null; then
        echo "docker compose"
    else
        echo "docker-compose"
    fi
}

# 检查环境文件
check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        print_warning ".env 文件不存在"
        if [ -f "$ENV_EXAMPLE" ]; then
            print_info "从 .env.example 复制配置..."
            cp "$ENV_EXAMPLE" "$ENV_FILE"
            print_success ".env 文件已创建，请根据需要修改配置"
        else
            print_error ".env.example 文件不存在，请手动创建 .env 文件"
            exit 1
        fi
    fi
}

# 初始化环境
init_env() {
    print_info "初始化环境..."
    
    if [ -f "$ENV_FILE" ]; then
        read -p ".env 文件已存在，是否覆盖？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "取消初始化"
            return
        fi
    fi
    
    if [ -f "$ENV_EXAMPLE" ]; then
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        print_success ".env 文件已创建"
    else
        print_error ".env.example 文件不存在"
        exit 1
    fi
    
    # 提示用户修改配置
    print_warning "请编辑 .env 文件配置以下重要参数："
    echo "  - POSTGRES_PASSWORD: 数据库密码"
    echo "  - AI_API_KEY: AI 服务 API 密钥"
    echo "  - JWT_SECRET: JWT 密钥"
}

# 启动服务
start_services() {
    local env_type="${1:-dev}"
    
    print_info "启动服务 (环境: $env_type)..."
    
    check_dependencies
    check_env_file
    
    local compose_cmd=$(get_compose_cmd)
    
    # 开发环境使用两个配置文件
    if [ "$env_type" = "dev" ] && [ -f "$COMPOSE_DEV_FILE" ]; then
        print_info "使用开发环境配置"
        print_info "拉取最新镜像..."
        $compose_cmd -f "$COMPOSE_FILE" -f "$COMPOSE_DEV_FILE" pull 2>/dev/null || true
        
        print_info "启动服务..."
        $compose_cmd -f "$COMPOSE_FILE" -f "$COMPOSE_DEV_FILE" up -d
    else
        print_info "拉取最新镜像..."
        $compose_cmd -f "$COMPOSE_FILE" pull 2>/dev/null || true
        
        print_info "启动服务..."
        $compose_cmd -f "$COMPOSE_FILE" up -d
    fi
    
    print_success "服务启动完成"
    print_info "等待服务就绪..."
    sleep 5
    
    show_status
}

# 停止服务
stop_services() {
    print_info "停止服务..."
    
    local compose_cmd=$(get_compose_cmd)
    
    # 停止开发环境
    if [ -f "$COMPOSE_DEV_FILE" ]; then
        $compose_cmd -f "$COMPOSE_FILE" -f "$COMPOSE_DEV_FILE" down 2>/dev/null || true
    fi
    
    # 停止生产环境
    $compose_cmd -f "$COMPOSE_FILE" down
    
    print_success "服务已停止"
}

# 重启服务
restart_services() {
    local env_type="${1:-dev}"
    
    print_info "重启服务..."
    stop_services
    start_services "$env_type"
}

# 查看服务状态
show_status() {
    print_info "服务状态:"
    echo ""
    
    local compose_cmd=$(get_compose_cmd)
    
    $compose_cmd -f "$COMPOSE_FILE" ps
}

# 查看日志
show_logs() {
    local service="$1"
    local compose_cmd=$(get_compose_cmd)
    
    if [ -z "$service" ]; then
        $compose_cmd -f "$COMPOSE_FILE" logs -f --tail=100
    else
        $compose_cmd -f "$COMPOSE_FILE" logs -f --tail=100 "$service"
    fi
}

# 构建镜像
build_images() {
    local env_type="${1:-dev}"
    
    print_info "构建镜像 (环境: $env_type)..."
    
    check_dependencies
    
    local compose_cmd=$(get_compose_cmd)
    
    # 构建时始终使用主配置文件
    $compose_cmd -f "$COMPOSE_FILE" build --no-cache
    
    print_success "镜像构建完成"
}

# 清理
clean_all() {
    print_warning "这将删除所有容器、镜像和数据卷！"
    read -p "确定要继续吗？(y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "取消清理"
        return
    fi
    
    print_info "清理中..."
    
    local compose_cmd=$(get_compose_cmd)
    
    # 停止并删除容器
    $compose_cmd -f "$COMPOSE_FILE" down -v --rmi all 2>/dev/null || true
    
    if [ -f "$COMPOSE_DEV_FILE" ]; then
        $compose_cmd -f "$COMPOSE_DEV_FILE" down -v --rmi all 2>/dev/null || true
    fi
    
    # 清理悬空镜像和容器
    docker system prune -af --volumes
    
    print_success "清理完成"
}

# 备份数据库
backup_database() {
    print_info "备份数据库..."
    
    local backup_dir="$PROJECT_ROOT/backups"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$backup_dir/campus_backup_$timestamp.sql"
    
    mkdir -p "$backup_dir"
    
    local compose_cmd=$(get_compose_cmd)
    
    # 检查 postgres 容器是否运行
    if ! $compose_cmd -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
        print_error "PostgreSQL 容器未运行"
        exit 1
    fi
    
    # 执行备份
    docker exec campus-postgres pg_dumpall -U campus > "$backup_file"
    
    # 压缩备份文件
    gzip "$backup_file"
    
    print_success "数据库备份完成: ${backup_file}.gz"
    
    # 清理旧备份（保留最近7个）
    ls -t "$backup_dir"/campus_backup_*.sql.gz 2>/dev/null | tail -n +8 | xargs -r rm
    
    print_info "旧备份已清理（保留最近7个）"
}

# 恢复数据库
restore_database() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        print_error "请指定备份文件"
        echo "用法: $0 restore <备份文件路径>"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        print_error "备份文件不存在: $backup_file"
        exit 1
    fi
    
    print_warning "这将覆盖当前数据库！"
    read -p "确定要继续吗？(y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "取消恢复"
        return
    fi
    
    print_info "恢复数据库..."
    
    local compose_cmd=$(get_compose_cmd)
    
    # 检查 postgres 容器是否运行
    if ! $compose_cmd -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
        print_error "PostgreSQL 容器未运行"
        exit 1
    fi
    
    # 如果是压缩文件，先解压
    if [[ "$backup_file" == *.gz ]]; then
        local temp_file="${backup_file%.gz}"
        gunzip -c "$backup_file" > "$temp_file"
        backup_file="$temp_file"
    fi
    
    # 执行恢复
    cat "$backup_file" | docker exec -i campus-postgres psql -U campus
    
    # 清理解压的临时文件
    if [ -n "$temp_file" ]; then
        rm "$temp_file"
    fi
    
    print_success "数据库恢复完成"
}

# 主函数
main() {
    local command="${1:-help}"
    local option="${2:-dev}"
    
    case "$command" in
        start)
            start_services "$option"
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services "$option"
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$option"
            ;;
        build)
            build_images "$option"
            ;;
        clean)
            clean_all
            ;;
        init)
            init_env
            ;;
        backup)
            backup_database
            ;;
        restore)
            restore_database "$option"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
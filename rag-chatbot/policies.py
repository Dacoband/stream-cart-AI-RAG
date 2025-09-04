# -*- coding: utf-8 -*-
"""
StreamCart Platform Policies
Chính sách Mua hàng và Bán hàng của nền tảng StreamCart
"""

PURCHASE_POLICY = """
🛒 CHÍNH SÁCH MUA HÀNG

1. ĐIỀU KIỆN MUA HÀNG
• Khách hàng phải có tài khoản hợp lệ, đã xác thực email/số điện thoại
• Tài khoản bị khóa hoặc chưa kích hoạt sẽ không thể đặt hàng
• Cung cấp thông tin đầy đủ và chính xác

2. QUY TRÌNH ĐẶT HÀNG
• Chỉ có thể đặt sản phẩm còn hàng và đang ở trạng thái "đang bán"
• Hệ thống tự động tính toán giá cuối cùng (giá gốc + giảm giá + phí vận chuyển)
• Sau khi đặt hàng, nhận thông tin chi tiết qua email/thông báo
• Phải xác nhận đơn hàng trước khi thanh toán

3. THANH TOÁN
• Hình thức: Online (qua cổng thanh toán) hoặc COD (thanh toán khi nhận hàng)
• Đơn hàng chỉ xác nhận khi thanh toán thành công hoặc xác nhận COD
• Thanh toán thất bại → đơn hàng tự động hủy sau 30 phút
• Tuân thủ chuẩn bảo mật PCI DSS

4. VẬN CHUYỂN & GIAO HÀNG
• Cung cấp địa chỉ giao hàng hợp lệ và chính xác
• Theo dõi trạng thái đơn hàng theo thời gian thực
• Trạng thái: Pending → Processing → Shipping → Completed/Canceled
• Giao không thành công nhiều lần → có thể bị hủy đơn

5. ĐỔI TRẢ & HOÀN TIỀN
• Áp dụng đổi trả trong thời hạn chính sách của shop (thường 3 ngày từ ngày giao thành công)
• Sản phẩm phải còn nguyên tem, nhãn mác, chưa qua sử dụng (trừ sản phẩm lỗi)
• Tiền hoàn trả theo phương thức thanh toán ban đầu
• Hệ thống ghi nhận lịch sử để phòng tránh gian lận

6. QUYỀN & NGHĨA VỤ KHÁCH HÀNG
Quyền:
• Khiếu nại khi sản phẩm sai mô tả, lỗi hoặc giao không đúng cam kết
• Theo dõi đơn hàng và yêu cầu hỗ trợ

Nghĩa vụ:
• Bảo mật thông tin tài khoản, không chia sẻ mật khẩu
• Thanh toán đầy đủ và đúng hạn
• Không lợi dụng chính sách đổi trả/hoàn tiền để trục lợi
"""

SALES_POLICY = """
🏪 CHÍNH SÁCH BÁN HÀNG

1. ĐIỀU KIỆN MỞ SHOP
• Đăng ký shop với thông tin đầy đủ (tên, địa chỉ, số điện thoại)
• Shop phải được Admin duyệt trước khi bắt đầu kinh doanh
• Mỗi tài khoản chỉ được quản lý một shop duy nhất

2. QUẢN LÝ SẢN PHẨM
• Chỉ được đăng bán sản phẩm thuộc danh mục hệ thống hỗ trợ
• Thông tin sản phẩm phải chính xác: tên, mô tả, giá, tồn kho, hình ảnh
• Hệ thống tự động tính số lượng đã bán và cập nhật tồn kho
• Không được chỉnh sửa lịch sử giao dịch đã hoàn tất
• Chỉ bán sản phẩm hợp pháp, không vi phạm quy định

3. XỬ LÝ ĐỠN HÀNG
• Xác nhận đơn hàng trong 1 ngày
• Chuẩn bị và đóng gói hàng trong 1 ngày
• Bàn giao cho đơn vị vận chuyển đúng thời hạn
• Cập nhật trạng thái đơn hàng thường xuyên

4. CHÍNH SÁCH GIÁ & KHUYẾN MÃI
• Được đặt giá gốc, giá khuyến mãi và mức giảm phần trăm
• Giá hiển thị cho khách luôn là giá cuối cùng đã áp dụng giảm giá
• Chương trình khuyến mãi phải qua duyệt trước khi áp dụng

5. TRÁCH NHIỆM & NGHĨA VỤ
• Cung cấp sản phẩm đúng mô tả, đúng chất lượng
• Không bán hàng giả, hàng nhái
• Chấp hành quy định về đổi trả và hỗ trợ khách hàng
• Tuân thủ chính sách về thuế, hóa đơn và pháp luật thương mại điện tử

6. XỬ LÝ VI PHẠM
Vi phạm (gian lận, bán hàng giả, sai mô tả, giao chậm nhiều lần):
• Mức 1: Cảnh cáo
• Mức 2: Tạm ngưng hoạt động
• Mức 3: Đóng cửa shop vĩnh viễn
• Các trường hợp nghiêm trọng: xử lý theo pháp luật
"""

GENERAL_TERMS = """
📋 ĐIỀU KHOẢN CHUNG

• Cả khách hàng và người bán phải tuân thủ đầy đủ quy định của hệ thống
• Mọi giao dịch được ghi nhận và có thể dùng làm bằng chứng khi tranh chấp
• Hệ thống có quyền điều chỉnh chính sách để phù hợp tình hình thực tế
• Đảm bảo công bằng và bảo vệ quyền lợi cho cả hai bên
• Hỗ trợ khách hàng: 8h-22h hàng ngày qua chat trực tiếp hoặc mục Trợ giúp
"""

def get_purchase_policy():
    """Lấy chính sách mua hàng"""
    return PURCHASE_POLICY

def get_sales_policy():
    """Lấy chính sách bán hàng"""
    return SALES_POLICY

def get_general_terms():
    """Lấy điều khoản chung"""
    return GENERAL_TERMS

def get_full_policy():
    """Lấy toàn bộ chính sách"""
    return f"{PURCHASE_POLICY}\n\n{SALES_POLICY}\n\n{GENERAL_TERMS}"

def search_policy(query: str) -> str:
    """Tìm kiếm thông tin chính sách dựa trên từ khóa"""
    query_lower = query.lower()
    
    # Mapping keywords to specific policy sections
    policy_keywords = {
        'mua hàng': PURCHASE_POLICY,
        'đặt hàng': PURCHASE_POLICY,
        'thanh toán': PURCHASE_POLICY,
        'giao hàng': PURCHASE_POLICY,
        'vận chuyển': PURCHASE_POLICY,
        'đổi trả': PURCHASE_POLICY,
        'hoàn tiền': PURCHASE_POLICY,
        'bán hàng': SALES_POLICY,
        'mở shop': SALES_POLICY,
        'đăng ký shop': SALES_POLICY,
        'quản lý sản phẩm': SALES_POLICY,
        'xử lý đơn hàng': SALES_POLICY,
        'vi phạm': SALES_POLICY,
        'khuyến mãi': SALES_POLICY,
        'chính sách giá': SALES_POLICY
    }
    
    # Find matching policies
    results = []
    for keyword, policy in policy_keywords.items():
        if keyword in query_lower and policy not in results:
            results.append(policy)
    
    if not results:
        return get_full_policy()
    
    return '\n\n'.join(results)
